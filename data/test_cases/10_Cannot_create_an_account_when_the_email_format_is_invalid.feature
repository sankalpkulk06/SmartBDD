# language: en
Feature: Cannot create an account when the email format is invalid

	Scenario Outline: Cannot create an account when the email format is invalid
		Given I am on the "AccountCreation" page
		When I fill AccountCreation fields with gender <gender> firstName <first> lastName <last> password <password> email <mail> birthDate <birth> acceptPartnerOffers <offers> acceptPrivacyPolicy <privacy> acceptNewsletter <news> acceptGdpr <gdpr> and submit
		Then I should still be on the "AccountCreation" page
		And An error message should be associated with the field <field>

		@01
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "02/08/1956" | "email_txt" | "Bob" | "yes" | "M" | "Vance" | "mail.fr" | "yes" | "yes" | "Bob1234" | "yes" |

		@02
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "02/08/1968" | "email_txt" | "Phyllis" | "yes" | "F" | "Vance" | "anemail @mailf.fr" | "yes" | "yes" | "Phyllis1234" | "yes" |

		@03
		Examples:
		| birth | field | first | gdpr | gender | last | mail | news | offers | password | privacy |
		| "05/07/1984" | "email_txt" | "Oscar" | "yes" | "M" | "Smith" | "youhùuu@mail.com" | "yes" | "yes" | "Oscar4321" | "yes" |