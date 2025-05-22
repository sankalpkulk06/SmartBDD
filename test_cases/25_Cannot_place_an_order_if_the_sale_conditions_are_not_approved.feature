# language: en
Feature: Cannot place an order if the sale conditions are not approved

	Scenario: Cannot place an order if the sale conditions are not approved
		Given I created an account with gender "M" firstName "john" lastName "doe" email "johndoe@mail.com" password "pass1234" birthDate "01/01/1950" partnerOffers "yes" newsletter "yes"
		And I am logged in with email "johndoe@mail.com" and password "pass1234"
		And The cart contains
			| Product | Number |
			| Mug The best is yet to come | 3 |
			| Illustration vectorielle Renard | 2 |
		And I am on the "Cart" page
		When I initiate order placement process
		And I fill command form with alias "add1" company "" vat "" address "1 rue du chat" supp "" zip "12345" city "Paris" country "France" phone "" and facturation "yes" and submit
		And I choose delivery "prestashop" and command message ""
		And I pay by paymode "virement bancaire" and choose approveSalesConditions "no"
		Then I should still be on the "Order" page
		And The submit order button should be disabled