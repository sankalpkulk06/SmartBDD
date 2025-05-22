# language: en
Feature: Place an order - logged-in customer

	Scenario Outline: Place an order - logged-in customer
		Given I created an account with gender "M" firstName "john" lastName "doe" email "johndoe@mail.com" password "pass1234" birthDate "01/01/1950" partnerOffers "yes" newsletter "yes"
		And I am logged in with email "johndoe@mail.com" and password "pass1234"
		And The cart contains
			| Product | Number |
			| Mug The best is yet to come | 3 |
			| Illustration vectorielle Renard | 2 |
		And I am on the "Cart" page
		When I initiate order placement process
		And I fill command form with alias <alias> company <company> vat <vat> address <address> supp <supp> zip <zip> city <city> country <country> phone <phone> and facturation "yes" and submit
		And I choose delivery <delivery> and command message <message>
		And I pay by paymode <paymode> and choose approveSalesConditions "yes"
		And I submit order
		Then The order should be placed and it should contain
			| Product | Number | UnitPrice |
			| Mug The best is yet to come | 3 | 14,28 |
			| Illustration vectorielle Renard | 2 | 10,80 |
		And The total order price should be <total_price>

		@01
		Examples:
			| address | alias | city | company | country | delivery | message | paymode | phone | supp | total_price | vat | zip |
			| "1234 oxford street" | "Add01" | "Paris" | "Dunder Mifflin" | "France" | "My carrier" | "Sonnette cassée, merci de téléphoner." | "chèque" | 123456789 | "1st floor" | 72,84 | "123456" | 12345 |

		@02
		Examples:
			| address | alias | city | company | country | delivery | message | paymode | phone | supp | total_price | vat | zip |
			| "1234 oxford street" | "" | "Paris" | "" | "France" | "My carrier" | "" | "chèque" | 987654321 | "" | 72,84 | "" | 12345 |