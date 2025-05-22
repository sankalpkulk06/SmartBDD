# language: en
Feature: Add one product to the cart

	Scenario: Add one product to the cart
		Given I am logged in
		And I am on the "Home" page
		When I navigate to category "art"
		And I navigate to product "Affiche encadrée The best is yet to come"
		And I add to cart
		Then The cart should contain
			| Product | Number | Dimension |
			| Affiche encadrée The best is yet to come | 1 | 40x60cm |