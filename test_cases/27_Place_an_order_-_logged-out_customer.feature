# language: en
Feature: Place an order - logged-out customer

	Scenario Outline: Place an order - logged-out customer
		Given I created an account with gender "M" firstName "john" lastName "doe" email "johndoe@mail.com" password "pass1234" birthDate "01/01/1950" partnerOffers "yes" newsletter "yes"
		And I am logged out
		And I am on the "Home" page
		When I navigate to category "accessoires"
		And I navigate to product "Mug The best is yet to come"
		And I add to cart
		And I navigate to the "Cart" page
		And I initiate order placement process
		And I fill login form with email "johndoe@mail.com" and password "pass1234"
		And I fill command form with alias <alias> company <company> vat <vat> address <address> supp <supp> zip <zip> city <city> country <country> phone <phone> and facturation "yes" and submit
		And I choose delivery <delivery> and command message <message>
		And I pay by paymode <paymode> and choose approveSalesConditions "yes"
		And I submit order
		Then The order should be placed and it should contain
			| Product | Number | UnitPrice |
			| Mug The best is yet to come | 1 | 14,28 |
		And The total order price should be <total_price>

		@01
		Examples:
			| address | alias | city | company | country | delivery | message | paymode | phone | supp | total_price | vat | zip |
			| "1234 oxford street" | "Add01" | "Paris" | "Dunder Mifflin" | "France" | "My carrier" | "Sonnette cassée, merci de téléphoner." | "chèque" | 123456789 | "1st floor" | 22,68 | 123456 | 12345 |