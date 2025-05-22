# language: en
Feature: Cannot add a product to the cart if the quantity exceeds stock

	Scenario: Cannot add a product to the cart if the quantity exceeds stock
		Given I am logged out
		And I am on the "Home" page
		When I navigate to category "accessoires"
		And I navigate to product "Mug Today is a good day"
		And I update quantity to "1599"
		Then The warning message "Le stock est insuffisant." should be displayed
		And I should not be able to add to cart