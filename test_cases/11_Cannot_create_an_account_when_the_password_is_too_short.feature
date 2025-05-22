# language: en
Feature: Cannot create an account when the password is too short

	Scenario: Cannot create an account when the password is too short
		Given I am on the "AccountCreation" page
		When I fill AccountCreation fields with gender "F" firstName "Niloofar" lastName "Norooz" password "word" email "niloofar@mail.com" birthDate "01/08/1993" acceptPartnerOffers "yes" acceptPrivacyPolicy "yes" acceptNewsletter "yes" acceptGdpr "yes" and submit
		Then I should still be on the "AccountCreation" page
		And An error message should be associated with the field "password_txt"