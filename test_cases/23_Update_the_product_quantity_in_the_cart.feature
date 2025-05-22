# language: en
Feature: Update the product quantity in the cart

	Scenario: Update the product quantity in the cart
		Given I am logged in
		And The cart contains
			| Product | Number |
			| Mug The best is yet to come | 5 |
			| Illustration vectorielle Renard | 1 |
		And I am on the "Cart" page
		When I update product quantities to
			| Product | Number |
			| Mug The best is yet to come | 3 |
			| Illustration vectorielle Renard | 4 |
		Then The cart should contain
			| Product | Number | UnitPrice | TotalProductPrice |
			| Mug The best is yet to come | 3 | 14,28 | 42,84 |
			| Illustration vectorielle Renard | 4 | 10,80 | 43,20 |
		And The total number of products should be "7" and the total price should be "86,04"