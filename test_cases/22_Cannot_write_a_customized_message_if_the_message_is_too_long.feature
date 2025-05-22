# language: en
Feature: Cannot write a customized message if the message is too long

	Scenario: Cannot write a customized message if the message is too long
		Given I am logged out
		And I am on the "Home" page
		When I navigate to category "accessoires"
		And I navigate to product "Mug personnalisable"
		And I customize with message
			"""
			Un très long message qui dépasse les 250 caractères maximum autorisés.
			Un très long message qui dépasse les 250 caractères maximum autorisés.
			Un très long message qui dépasse les 250 caractères maximum autorisés.
			Un très long message qui dépasse les 250 caractères maximum autorisés.
			"""
		Then The customized message should be
			"""
			Un très long message qui dépasse les 250 caractères maximum autorisés. Un très long message qui dépasse les 250 caractères maximum autorisés. Un très long message qui dépasse les 250 caractères maximum autorisés. Un très long message qui dépasse les
			"""