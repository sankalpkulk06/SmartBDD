# language: en
Feature: Modify the account information

	Scenario Outline: Modify the account information
		Given I created an account with gender "M" firstName "john" lastName "doe" email "johndoe@mail.com" password "pass1234" birthDate "01/01/1950" partnerOffers "yes" newsletter "yes"
		And I am logged in with email "johndoe@mail.com" and password "pass1234"
		And I am on the "MyIdentity" page
		When I fill MyIdentity fields with gender <gender> firstName <first> lastName <last> email <mail> oldPass "pass1234" newPass <password> birthDate <birth> partnerOffers <offers> privacyPolicy "yes" newsletter <news> gdpr "yes" and submit
		Then The message "Information mise à jour avec succès." should be displayed
		And My personal information should be gender <gender> firstName <first> lastName <last> email <mail> birthDate <birth> acceptPartnerOffers <offers> acceptPrivacyPolicy "no" acceptNewsletter <news> acceptGdpr "no"

		@01
		Examples:
		| birth | first | gender | last | mail | news | offers | password |
		| "15/12/1978" | "Angela" | "F" | "Hamilton" | "angela@mail.com" | "yes" | "yes" | "angela1234" |

		@02
		Examples:
		| birth | first | gender | last | mail | news | offers | password |
		| "08/11/1968" | "Dwight" | "M" | "Smith" | "dwight1234@mail.com" | "no" | "no" | "pass4563" |