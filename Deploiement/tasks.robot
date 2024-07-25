*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${URL}          https://www.vabf.almerys.com/CZ-J/0/valerys/
${USERNAME}     SAT201
${PASSWORD}     Almerys0
${LOGIN_SELECTOR}  css=input[type='submit'] 
${SUCCESS_SELECTOR}    xpath=//ul[contains(@class, 'topMenuIcons') and contains(@class, 'floatLeft')]
*** Test Cases ***
Test Adele
    Open The Intranet Website
    Log In
    Check Login Success
    Collect Results

*** Keywords ***
Open The Intranet Website
    [Documentation]    Navigates to the given URL
    Open Browser    ${URL}    chrome
    Maximize Browser Window

Log In
    [Documentation]    Fills in the login form and clicks the 'Log in' button
    Input Text    name=username    ${USERNAME}
    Input Text    name=password    ${PASSWORD}
    Wait Until Element Is Visible    ${LOGIN_SELECTOR}    10 seconds
    Click Element    ${LOGIN_SELECTOR}

Check Login Success
    [Documentation]    Checks if login was successful by waiting for a specific element
    Wait Until Element Is Visible    ${SUCCESS_SELECTOR}    30 seconds
    Log    Connexion réussie!

Collect Results
    [Documentation]    Take a screenshot of the page
    Sleep    3s
    Close Browser
