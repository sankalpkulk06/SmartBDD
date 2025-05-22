# language: en
Feature: Cannot create an account when privacy and/or GDPR are not checked

	Scenario Outline: Cannot create an account when privacy and/or GDPR are not checked
		Given I am on the "AccountCreation" page
		When I fill AccountCreation fields with gender <gender> firstName <first> lastName <last> password <password> email <mail> birthDate <birth> acceptPartnerOffers <offers> acceptPrivacyPolicy <privacy> acceptNewsletter <news> acceptGdpr <gdpr> and submit
		Then I should still be on the "AccountCreation" page
		And An error message should be associated with the field <field>

		@01-privacy_is_no
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "02/08/1997" | "privacy_cb" | "Pam" | "yes" | "F" | "Johnson" | "pam@mail.com" | "yes" | "yes" | "pam12pam" | "no" |

		@02-gdpr_is_no
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "05/07/1993" | "gdpr_cb" | "Jim" | "no" | "M" | "Jones" | "jim@email.com" | "yes" | "yes" | "jim8528" | "yes" |