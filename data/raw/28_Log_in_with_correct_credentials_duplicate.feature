# language: en
Feature: Log in with correct credentials

	Scenario: Log in with correct credentials
		Given I created an account with gender "F" firstName "Mary" lastName "Smith" email "marysmith@example.com" password "smitty4life" birthDate "01/01/2000" partnerOffers "yes" newsletter "yes"
		And I am logged out
		And I am on the "Login" page
		When I log in with email "marysmith@example.com" and password "smitty4life"
		Then I can see firstName and lastName "Mary Smith" in the top right corner
