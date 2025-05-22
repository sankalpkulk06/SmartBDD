# language: en
Feature: Create an account

	Scenario Outline: Create an account
		Given I am on the "AccountCreation" page
		When I fill AccountCreation fields with gender <gender> firstName <first> lastName <last> password <password> email <mail> birthDate <birth> acceptPartnerOffers <offers> acceptPrivacyPolicy "yes" acceptNewsletter <news> acceptGdpr "yes" and submit
		And I log out
		And I navigate to the "Login" page
		And I log in with email <mail> and password <password>
		Then My personal information should be gender <gender> firstName <first> lastName <last> email <mail> birthDate <birth> acceptPartnerOffers <offers> acceptPrivacyPolicy "no" acceptNewsletter <news> acceptGdpr "no"

		@01
		Examples:
		| birth | first | gender | last | mail | news | offers | password |
		| "01/01/1980" | "John" | "M" | "Doe" | "john.doe@letter.fr" | "yes" | "yes" | "Pass1234" |

		@02
		Examples:
		| birth | first | gender | last | mail | news | offers | password |
		| "25/12/1996" | "Jane" | "F" | "Doe" | "jane.doe@letter.fr" | "no" | "no" | "12$µi" |

		@03
		Examples:
		| birth | first | gender | last | mail | news | offers | password |
		| "01/10/2000" | "Noël" | "U" | "Merry" | "unmail@mail.mail" | "yes" | "yes" | "ViveLesSapins_1234" |