# language: en
Feature: Cannot modify the account information when privacy and/or GDPR are not checked

	Scenario Outline: Cannot modify the account information when privacy and/or GDPR are not checked
		Given I created an account with gender "M" firstName "john" lastName "doe" email "johndoe@mail.com" password "pass1234" birthDate "01/01/1950" partnerOffers "yes" newsletter "yes"
		And I am logged in with email "johndoe@mail.com" and password "pass1234"
		And I am on the "MyIdentity" page
		When I fill MyIdentity fields with gender <gender> firstName <first> lastName <last> email <mail> oldPass "pass1234" newPass <password> birthDate <birth> partnerOffers <offers> privacyPolicy <privacy> newsletter <news> gdpr <gdpr> and submit
		Then I should still be on the "MyIdentity" page
		And An error message should be associated with the field <field>

		@01-privacy_is_no
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "01/01/1990" | "privacy_cb" | "Alice" | "yes" | "F" | "NOËL" | "alice.noel@mail.com" | "yes" | "yes" | "Pass4321" | "no" |

		@02-gdpr_is_no
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "02/02/1989" | "gdpr_cb" | "Bob" | "no" | "M" | "leon" | "bob.leon@mail.com" | "yes" | "yes" | "Pass1234" | "yes" |