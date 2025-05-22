# language: en
Feature: Add one product with a customized message to the cart

	Scenario: Add one product with a customized message to the cart
		Given I am logged out
		And I am on the "Home" page
		When I navigate to category "accessoires"
		And I navigate to product "Mug personnalisable"
		And I customize with message "Joyeux anniversaire"
		And I add to cart
		Then The cart should contain
			| Product | Number | Customization |
			| Mug personnalisable | 1 | Joyeux anniversaire |