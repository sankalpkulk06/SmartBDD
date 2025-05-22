# language: en
Feature: Cannot log in with an incorrect password

	Scenario: Cannot log in with an incorrect password
		Given I created an account with gender "F" firstName "Alice" lastName "Noel" email "alice@noel.com" password "police" birthDate "01/01/1970" partnerOffers "yes" newsletter "yes"
		And I am logged out
		And I am on the "Login" page
		When I log in with email "alice@noel.com" and password "poluce"
		Then I should still be on the "Login" page
		And The error message "Échec d'authentification" should be displayed