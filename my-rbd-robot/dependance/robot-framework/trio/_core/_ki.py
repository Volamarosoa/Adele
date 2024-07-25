from __future__ import annotations

import inspect
import signal
import sys
from functools import wraps
from typing import TYPE_CHECKING, Final, Protocol, TypeVar

import attrs

from .._util import is_main_thread

CallableT = TypeVar("CallableT", bound="Callable[..., object]")
RetT = TypeVar("RetT")

if TYPE_CHECKING:
    import types
    from collections.abc import Callable

    from typing_extensions import ParamSpec, TypeGuard

    ArgsT = ParamSpec("ArgsT")

# In ordinary single-threaded Python code, when you hit control-C, it raises
# an exception and automatically does all the regular unwinding stuff.
#
# In Trio code, we would like hitting control-C to raise an exception and
# automatically do all the regular unwinding stuff. In particular, we would
# like to maintain our invariant that all tasks always run to completion (one
# way or another), by unwinding all of them.
#
# But it's basically impossible to write the core task running code in such a
# way that it can maintain this invariant in the face of KeyboardInterrupt
# exceptions arising at arbitrary bytecode positions. Similarly, if a
# KeyboardInterrupt happened at the wrong moment inside pretty much any of our
# inter-task synchronization or I/O primitives, then the system state could
# get corrupted and prevent our being able to clean up properly.
#
# So, we need a way to defer KeyboardInterrupt processing from these critical
# sections.
#
# Things that don't work:
#
# - Listen for SIGINT and process it in a system task: works fine for
#   well-behaved programs that regularly pass through the event loop, but if
#   user-code goes into an infinite loop then it can't be interrupted. Which
#   is unfortunate, since dealing with infinite loops is what
#   KeyboardInterrupt is for!
#
# - Use pthread_sigmask to disable signal delivery during critical section:
#   (a) windows has no pthread_sigmask, (b) python threads start with all
#   signals unblocked, so if there are any threads around they'll receive the
#   signal and then tell the main thread to run the handler, even if the main
#   thread has that signal blocked.
#
# - Install a signal handler which checks a global variable to decide whether
#   to raise the exception immediately (if we're in a non-critical section),
#   or to schedule it on the event loop (if we're in a critical section). The
#   problem here is that it's impossible to transition safely out of user code:
#
#     with keyboard_interrupt_enabled:
#         msg = coro.send(value)
#
#   If this raises a KeyboardInterrupt, it might be because the coroutine got
#   interrupted and has unwound... or it might be the KeyboardInterrupt
#   arrived just *after* 'send' returned, so the coroutine is still running,
#   but we just lost the message it sent. (And worse, in our actual task
#   runner, the send is hidden inside a utility function etc.)
#
# Solution:
#
# Mark *stack frames* as being interrupt-safe or interrupt-unsafe, and from
# the signal handler check which kind of frame we're currently in when
# deciding whether to raise or schedule the exception.
#
# There are still some cases where this can fail, like if someone hits
# control-C while the process is in the event loop, and then it immediately
# enters an infinite loop in user code. In this case the user has to hit
# control-C a second time. And of course if the user code is written so that
# it doesn't actually exit after a task crashes and everything gets cancelled,
# then there's not much to be done. (Hitting control-C repeatedly might help,
# but in general the solution is to kill the process some other way, just like
# for any Python program that's written to catch and ignore
# KeyboardInterrupt.)

# We use this special string as a unique key into the frame locals dictionary.
# The @ ensures it is not a valid identifier and can't clash with any possible
# real local name. See: https://github.com/python-trio/trio/issues/469
LOCALS_KEY_KI_PROTECTION_ENABLED: Final = "@TRIO_KI_PROTECTION_ENABLED"


# NB: according to the signal.signal docs, 'frame' can be None on entry to
# this function:
def ki_protection_enabled(frame: types.FrameType | None) -> bool:
    while frame is not None:
        if LOCALS_KEY_KI_PROTECTION_ENABLED in frame.f_locals:
            return bool(frame.f_locals[LOCALS_KEY_KI_PROTECTION_ENABLED])
        if frame.f_code.co_name == "__del__":
            return True
        frame = frame.f_back
    return True


def currently_ki_protected() -> bool:
    r"""Check whether the calling code has :exc:`KeyboardInterrupt` protection
    enabled.

    It's surprisingly easy to think that one's :exc:`KeyboardInterrupt`
    protection is enabled when it isn't, or vice-versa. This function tells
    you what Trio thinks of the matter, which makes it useful for ``assert``\s
    and unit tests.

    Returns:
      bool: True if protection is enabled, and False otherwise.

    """
    return ki_protection_enabled(sys._getframe())


# This is to support the async_generator package necessary for aclosing on <3.10
# functions decorated @async_generator are given this magic property that's a
# reference to the object itself
# see python-trio/async_generator/async_generator/_impl.py
def legacy_isasyncgenfunction(
    obj: object,
) -> TypeGuard[Callable[..., types.AsyncGeneratorType[object, object]]]:
    return getattr(obj, "_async_gen_function", None) == id(obj)


def _ki_protection_decorator(
    enabled: bool,
) -> Callable[[Callable[ArgsT, RetT]], Callable[ArgsT, RetT]]:
    # The "ignore[return-value]" below is because the inspect functions cast away the
    # original return type of fn, making it just CoroutineType[Any, Any, Any] etc.
    # ignore[misc] is because @wraps() is passed a callable with Any in the return type.
    def decorator(fn: Callable[ArgsT, RetT]) -> Callable[ArgsT, RetT]:
        # In some version of Python, isgeneratorfunction returns true for
        # coroutine functions, so we have to check for coroutine functions
        # first.
        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            def wrapper(*args: ArgsT.args, **kwargs: ArgsT.kwargs) -> RetT:  # type: ignore[misc]
                # See the comment for regular generators below
                coro = fn(*args, **kwargs)
                coro.cr_frame.f_locals[LOCALS_KEY_KI_PROTECTION_ENABLED] = enabled
                return coro  # type: ignore[return-value]

            return wrapper
        elif inspect.isgeneratorfunction(fn):

            @wraps(fn)
            def wrapper(*args: ArgsT.args, **kwargs: ArgsT.kwargs) -> RetT:  # type: ignore[misc]
                # It's important that we inject this directly into the
                # generator's locals, as opposed to setting it here and then
                # doing 'yield from'. The reason is, if a generator is
                # throw()n into, then it may magically pop to the top of the
                # stack. And @contextmanager generators in particular are a
                # case where we often want KI protection, and which are often
                # thrown into! See:
                #     https://bugs.python.org/issue29590
                gen = fn(*args, **kwargs)
                gen.gi_frame.f_locals[LOCALS_KEY_KI_PROTECTION_ENABLED] = enabled
                return gen  # type: ignore[return-value]

            return wrapper
        elif inspect.isasyncgenfunction(fn) or legacy_isasyncgenfunction(fn):

            @wraps(fn)  # type: ignore[arg-type]
            def wrapper(*args: ArgsT.args, **kwargs: ArgsT.kwargs) -> RetT:  # type: ignore[misc]
                # See the comment for regular generators above
                agen = fn(*args, **kwargs)
                agen.ag_frame.f_locals[LOCALS_KEY_KI_PROTECTION_ENABLED] = enabled
                return agen  # type: ignore[return-value]

            return wrapper
        else:

            @wraps(fn)
            def wrapper(*args: ArgsT.args, **kwargs: ArgsT.kwargs) -> RetT:
                sys._getframe().f_locals[LOCALS_KEY_KI_PROTECTION_ENABLED] = enabled
                return fn(*args, **kwargs)

            return wrapper

    return decorator


# pyright workaround: https://github.com/microsoft/pyright/issues/5866
class KIProtectionSignature(Protocol):
    __name__: str

    def __call__(self, f: CallableT, /) -> CallableT:
        pass


# the following `type: ignore`s are because we use ParamSpec internally, but want to allow overloads
enable_ki_protection: KIProtectionSignature = _ki_protection_decorator(True)  # type: ignore[assignment]
enable_ki_protection.__name__ = "enable_ki_protection"

disable_ki_protection: KIProtectionSignature = _ki_protection_decorator(False)  # type: ignore[assignment]
disable_ki_protection.__name__ = "disable_ki_protection"


@attrs.define(slots=False)
class KIManager:
    handler: Callable[[int, types.FrameType | None], None] | None = None

    def install(
        self,
        deliver_cb: Callable[[], object],
        restrict_keyboard_interrupt_to_checkpoints: bool,
    ) -> None:
        assert self.handler is None
        if (
            not is_main_thread()
            or signal.getsignal(signal.SIGINT) != signal.default_int_handler
        ):
            return

        def handler(signum: int, frame: types.FrameType | None) -> None:
            assert signum == signal.SIGINT
            protection_enabled = ki_protection_enabled(frame)
            if protection_enabled or restrict_keyboard_interrupt_to_checkpoints:
                deliver_cb()
            else:
                raise KeyboardInterrupt

        self.handler = handler
        signal.signal(signal.SIGINT, handler)

    def close(self) -> None:
        if self.handler is not None:
            if signal.getsignal(signal.SIGINT) is self.handler:
                signal.signal(signal.SIGINT, signal.default_int_handler)
            self.handler = None
