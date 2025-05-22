# language: en
Feature: Remove a product from the cart

	Scenario: Remove a product from the cart
		Given I am logged in
		And The cart contains
			| Product | Number |
			| Mug The best is yet to come | 5 |
			| Illustration vectorielle Renard | 1 |
		And I am on the "Cart" page
		When I remove product "Mug The best is yet to come"
		Then The cart should contain
			| Product | Number | UnitPrice |
			| Illustration vectorielle Renard | 1 | 10,80 |
		And The total number of products should be "1" and the total price should be "10,80"