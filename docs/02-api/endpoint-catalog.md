# Katalog endpointów Allegro REST API

> Plik generowany przez `scripts/build_api_catalog.py`. Nie edytuj ręcznie.

- źródło kontraktu: `https://developer.allegro.pl/swagger.yaml`
- odczytano: `2026-08-20T00:00:00+00:00`
- SHA-256 źródła: `a8ce81f568d9b97986360cc2a62c6708dbe23686051a6fbcf18244e6eb7cd1c8`
- OpenAPI: `3.0.0`
- wersja API: `latest`
- paths: **201**
- operations: **267**
- schemas: **967**
- deprecated operations: **6**

## Zakresy OAuth używane przez operacje

- `allegro:api:affiliate:read`
- `allegro:api:bids`
- `allegro:api:billing:read`
- `allegro:api:campaigns`
- `allegro:api:disputes`
- `allegro:api:fulfillment:read`
- `allegro:api:fulfillment:write`
- `allegro:api:messaging`
- `allegro:api:orders:read`
- `allegro:api:orders:write`
- `allegro:api:payments:read`
- `allegro:api:payments:write`
- `allegro:api:profile:read`
- `allegro:api:profile:write`
- `allegro:api:ratings`
- `allegro:api:sale:offers:read`
- `allegro:api:sale:offers:write`
- `allegro:api:sale:settings:read`
- `allegro:api:sale:settings:write`
- `allegro:api:shipments:read`
- `allegro:api:shipments:write`

## Liczba operacji według tagu

| Tag | Operacje |
|---|---:|
| Additional services | 5 |
| Additional services translations | 3 |
| Advance Ship Notices | 11 |
| After sale services | 15 |
| AlleDiscount | 7 |
| Allegro Prices | 7 |
| Auctions and Bidding | 2 |
| Automatic pricing | 6 |
| Badge campaigns | 7 |
| Batch offer modification | 15 |
| Billing | 2 |
| Categories and parameters | 6 |
| Charity | 1 |
| Classifieds | 6 |
| Commission refunds | 4 |
| Compatibility List | 4 |
| Contacts | 4 |
| Conversions | 1 |
| Customer returns | 3 |
| Delivery | 7 |
| Deposits | 1 |
| Flexible bundles | 5 |
| Fulfillment Parcels | 1 |
| Fulfillment Products | 1 |
| Fulfillment Removal | 2 |
| Fulfillment Returns | 1 |
| Fulfillment Stock | 1 |
| Images and attachments | 4 |
| Information about marketplaces | 1 |
| Information about user | 11 |
| Message Center | 11 |
| Offer bundles | 4 |
| Offer management | 16 |
| Offer rating | 1 |
| Offer tags | 6 |
| Offer translations | 3 |
| Order management | 15 |
| Payments | 3 |
| Points of service | 5 |
| Post Purchase Issues | 8 |
| Pricing | 2 |
| Products | 6 |
| Public user information | 1 |
| Rebates and promotions | 8 |
| Responsible persons | 3 |
| Responsible producers | 4 |
| Shipment management | 13 |
| Size tables | 5 |
| Tax Identification Number | 3 |
| Tax settings | 1 |
| User's offer information | 5 |

## Additional services

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offer-additional-services/categories` | `getListOfAdditionalServicesDefinitionsCategoriesUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403 | nie |
| GET | `/sale/offer-additional-services/groups` | `getListOfAdditionalServicesGroupsUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403 | nie |
| POST | `/sale/offer-additional-services/groups` | `createAdditionalServicesGroupUsingPOST` | `allegro:api:sale:settings:write` | 201, 401, 422 | nie |
| GET | `/sale/offer-additional-services/groups/{groupId}` | `getAdditionalServicesGroupUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 404 | nie |
| PUT | `/sale/offer-additional-services/groups/{groupId}` | `modifyAdditionalServicesGroupUsingPUT` | `allegro:api:sale:settings:write` | 200, 401, 404 | nie |

## Additional services translations

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offer-additional-services/groups/{groupId}/translations` | `getAdditionalServiceGroupTranslations` | `allegro:api:sale:settings:read` | 200, 401, 404 | nie |
| DELETE | `/sale/offer-additional-services/groups/{groupId}/translations/{language}` | `deleteAdditionalServiceGroupTranslation` | `allegro:api:sale:offers:write` | 204, 401, 403, 404 | nie |
| PATCH | `/sale/offer-additional-services/groups/{groupId}/translations/{language}` | `updateAdditionalServiceGroupTranslation` | `allegro:api:sale:settings:write` | 200, 401, 404 | nie |

## Advance Ship Notices

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/advance-ship-notices` | `getAdvanceShipNotices` | `allegro:api:fulfillment:read` | 200, 401, 403, 422 | nie |
| POST | `/fulfillment/advance-ship-notices` | `createAdvanceShipNotice` | `allegro:api:fulfillment:write` | 201, 400, 401, 403, 422 | nie |
| DELETE | `/fulfillment/advance-ship-notices/{id}` | `deleteAdvanceShipNotice` | `allegro:api:fulfillment:write` | 204, 401, 403, 404, 422 | nie |
| GET | `/fulfillment/advance-ship-notices/{id}` | `getAdvanceShipNotice` | `allegro:api:fulfillment:read` | 200, 401, 403, 404 | nie |
| PUT | `/fulfillment/advance-ship-notices/{id}` | `updateAdvanceShipNotice` | `allegro:api:fulfillment:write` | 200, 400, 401, 403, 412, 422 | nie |
| PUT | `/fulfillment/advance-ship-notices/{id}/cancel` | `cancelAdvanceShipNotice` | `allegro:api:fulfillment:write` | 200, 401, 403, 404, 422 | nie |
| GET | `/fulfillment/advance-ship-notices/{id}/labels` | `getAdvanceShipNoticeLabels` | `allegro:api:fulfillment:read` | 200, 401, 403, 404 | nie |
| GET | `/fulfillment/advance-ship-notices/{id}/receiving-state` | `getAdvanceShipNoticeReceivingState` | `allegro:api:fulfillment:read` | 200, 401, 403, 404 | nie |
| PUT | `/fulfillment/advance-ship-notices/{id}/submitted` | `updateSubmittedAdvanceShipNotice` | `allegro:api:fulfillment:write` | 200, 400, 401, 403, 412, 422 | nie |
| GET | `/fulfillment/submit-commands/{command-id}` | `getSubmitCommand` | `allegro:api:fulfillment:read` | 200, 401, 403, 422 | nie |
| PUT | `/fulfillment/submit-commands/{command-id}` | `submitCommand` | `allegro:api:fulfillment:write` | 201, 401, 422 | nie |

## After sale services

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| POST | `/after-sales-service-conditions/attachments` | `createAfterSalesServiceConditionsAttachmentUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 415, 422 | nie |
| PUT | `/after-sales-service-conditions/attachments/{attachmentId}` | `uploadAfterSalesServiceConditionsAttachmentUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 413, 422 | nie |
| GET | `/after-sales-service-conditions/implied-warranties` | `getPublicSellerListingUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| POST | `/after-sales-service-conditions/implied-warranties` | `createAfterSalesServiceImpliedWarrantyUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 422 | nie |
| GET | `/after-sales-service-conditions/implied-warranties/{impliedWarrantyId}` | `getAfterSalesServiceImpliedWarrantyUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/after-sales-service-conditions/implied-warranties/{impliedWarrantyId}` | `updateAfterSalesServiceImpliedWarrantyUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/after-sales-service-conditions/return-policies` | `getPublicSellerListingUsingGET_1` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| POST | `/after-sales-service-conditions/return-policies` | `createAfterSalesServiceReturnPolicyUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 422 | nie |
| DELETE | `/after-sales-service-conditions/return-policies/{returnPolicyId}` | `deleteAfterSalesServiceReturnPolicyUsingDELETE` | `allegro:api:sale:settings:write` | 200, 204, 400, 401, 403, 404 | nie |
| GET | `/after-sales-service-conditions/return-policies/{returnPolicyId}` | `getAfterSalesServiceReturnPolicyUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/after-sales-service-conditions/return-policies/{returnPolicyId}` | `updateAfterSalesServiceReturnPolicyUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/after-sales-service-conditions/warranties` | `getPublicSellerListingUsingGET_2` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| POST | `/after-sales-service-conditions/warranties` | `createAfterSalesServiceWarrantyUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 422 | nie |
| GET | `/after-sales-service-conditions/warranties/{warrantyId}` | `getAfterSalesServiceWarrantyUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/after-sales-service-conditions/warranties/{warrantyId}` | `updateAfterSalesServiceWarrantyUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 422 | nie |

## AlleDiscount

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/alle-discount/campaigns` | `getAlleDiscountCampaigns` | `allegro:api:campaigns` | 200, 400, 401, 404 | nie |
| POST | `/sale/alle-discount/submit-offer-commands` | `submitOfferToAlleDiscountCommands` | `allegro:api:campaigns` | 201, 400, 401, 409 | nie |
| GET | `/sale/alle-discount/submit-offer-commands/{commandId}` | `getSubmitOfferToAlleDiscountCommandsStatus` | `allegro:api:campaigns` | 200, 401, 404 | nie |
| POST | `/sale/alle-discount/withdraw-offer-commands` | `withdrawOfferFromAlleDiscountCommands` | `allegro:api:campaigns` | 201, 400, 401, 409 | nie |
| GET | `/sale/alle-discount/withdraw-offer-commands/{commandId}` | `getWithdrawOfferFromAlleDiscountCommandsStatus` | `allegro:api:campaigns` | 200, 401, 404 | nie |
| GET | `/sale/alle-discount/{campaignId}/eligible-offers` | `getOffersEligibleForAlleDiscount` | `allegro:api:campaigns` | 200, 400, 401, 403, 404 | nie |
| GET | `/sale/alle-discount/{campaignId}/submitted-offers` | `getOffersSubmittedToAlleDiscount` | `allegro:api:campaigns` | 200, 400, 401, 403, 404 | nie |

## Allegro Prices

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/allegro-prices/accounts/participations` | `getAccountParticipation` | `allegro:api:campaigns` | 200, 401 | nie |
| PATCH | `/sale/allegro-prices/accounts/participations` | `updateAccountParticipation` | `allegro:api:campaigns` | 200, 400, 401, 422 | nie |
| POST | `/sale/allegro-prices/offers-queries` | `getAllegroPricesOffers` | `allegro:api:campaigns` | 200, 400, 401, 422 | nie |
| POST | `/sale/allegro-prices/offers/exclusion-commands` | `excludeOfferCommands` | `allegro:api:campaigns` | 201, 400, 401, 409, 422 | nie |
| GET | `/sale/allegro-prices/offers/exclusion-commands/{commandId}` | `getExcludeOfferCommandStatus` | `allegro:api:campaigns` | 200, 400, 401, 404 | nie |
| POST | `/sale/allegro-prices/offers/submit-offer-commands` | `submitOfferCommands` | `allegro:api:campaigns` | 201, 400, 401, 409, 422 | nie |
| GET | `/sale/allegro-prices/offers/submit-offer-commands/{commandId}` | `getSubmitOfferCommandStatus` | `allegro:api:campaigns` | 200, 400, 401, 404 | nie |

## Auctions and Bidding

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/bidding/offers/{offerId}/bid` | `getBid` | `allegro:api:bids` | 200, 404 | nie |
| PUT | `/bidding/offers/{offerId}/bid` | `placeBid` | `allegro:api:bids` | 200, 400, 401, 404, 422 | nie |

## Automatic pricing

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/price-automation/offers/{offerId}/rules` | `getAutomaticPricingRulesForOfferUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| GET | `/sale/price-automation/rules` | `getAutomaticPricingRulesUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403 | nie |
| POST | `/sale/price-automation/rules` | `createAutomaticPricingRulesUsingPost` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 404, 409 | nie |
| DELETE | `/sale/price-automation/rules/{ruleId}` | `deleteAutomaticPricingRuleUsingDelete` | `allegro:api:sale:offers:write` | 204, 401, 403, 404 | nie |
| GET | `/sale/price-automation/rules/{ruleId}` | `getAutomaticPricingRuleByIdUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 404 | nie |
| PUT | `/sale/price-automation/rules/{ruleId}` | `updateAutomaticPricingRuleUsingPut` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 404, 409 | nie |

## Badge campaigns

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/badge-applications` | `badgeApplications_get_all` | `allegro:api:campaigns` | 200, 400, 401, 403 | nie |
| GET | `/sale/badge-applications/{applicationId}` | `badgeApplications_get_one` | `allegro:api:campaigns` | 200, 401, 403, 404 | nie |
| GET | `/sale/badge-campaigns` | `badgeCampaigns_get_all` | `allegro:api:campaigns` | 200, 400, 401, 403 | nie |
| GET | `/sale/badge-operations/{operationId}` | `badgeOperations_get_one` | `allegro:api:campaigns` | 200, 401, 403, 404 | nie |
| GET | `/sale/badges` | `getBadges` | `allegro:api:campaigns` | 200, 400, 401, 403 | nie |
| POST | `/sale/badges` | `postBadges` | `allegro:api:campaigns` | 202, 400, 401, 403, 422 | nie |
| PATCH | `/sale/badges/offers/{offerId}/campaigns/{campaignId}` | `patchBadge` | `allegro:api:campaigns` | 202, 400, 401, 403, 404, 409, 422 | nie |

## Batch offer modification

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| POST | `/sale/offer-bulk-modification-commands` | `batchOfferModificationUsingPOST` | `allegro:api:sale:offers:write` | 201, 400, 401, 409, 422 | nie |
| GET | `/sale/offer-bulk-modification-commands/{commandId}` | `batchOfferModificationCommandStatusUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404 | nie |
| GET | `/sale/offer-bulk-modification-commands/{commandId}/tasks` | `batchOfferModificationCommandTaskStatusesUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404, 422 | nie |
| GET | `/sale/offer-modification-commands/{commandId}` | `getGeneralReportUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 403, 404 | nie |
| PUT | `/sale/offer-modification-commands/{commandId}` | `modificationCommandUsingPUT` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 404, 409, 422 | nie |
| GET | `/sale/offer-modification-commands/{commandId}/tasks` | `getTasksUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 403, 404, 422 | nie |
| POST | `/sale/offer-price-automation-commands` | `offerAutomaticPricingModificationCommandUsingPOST` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 409, 422 | nie |
| GET | `/sale/offer-price-automation-commands/{commandId}` | `getofferAutomaticPricingModificationCommandStatusUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| GET | `/sale/offer-price-automation-commands/{commandId}/tasks` | `getofferAutomaticPricingModificationCommandTasksStatusesUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404, 422 | nie |
| GET | `/sale/offer-price-change-commands/{commandId}` | `getPriceModificationCommandStatusUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404 | nie |
| PUT | `/sale/offer-price-change-commands/{commandId}` | `priceModificationCommandUsingPUT` | `allegro:api:sale:offers:write` | 201, 400, 401, 409, 422 | nie |
| GET | `/sale/offer-price-change-commands/{commandId}/tasks` | `getPriceModificationCommandTasksStatusesUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404, 422 | nie |
| GET | `/sale/offer-quantity-change-commands/{commandId}` | `getQuantityModificationCommandStatusUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404 | nie |
| PUT | `/sale/offer-quantity-change-commands/{commandId}` | `quantityModificationCommandUsingPUT` | `allegro:api:sale:offers:write` | 201, 400, 401, 409, 422 | nie |
| GET | `/sale/offer-quantity-change-commands/{commandId}/tasks` | `getQuantityModificationCommandTasksStatusesUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 404, 422 | nie |

## Billing

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/billing/billing-entries` | `getBillingEntries` | `allegro:api:billing:read` | 200, 401, 406, 422 | nie |
| GET | `/billing/billing-types` | `getBillingTypes` | — | 200, 401 | nie |

## Categories and parameters

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/categories` | `getCategoriesUsingGET` | — | 200, 404 | nie |
| GET | `/sale/categories/{categoryId}` | `getCategoryUsingGET_1` | — | 200, 404 | nie |
| GET | `/sale/categories/{categoryId}/parameters` | `getFlatParametersUsingGET_2` | — | 200, 404 | nie |
| GET | `/sale/category-events` | `getCategoryEventsUsingGET_1` | — | 200, 400, 401 | nie |
| GET | `/sale/category-parameters-scheduled-changes` | `getCategoryParametersScheduledChangesUsingGET_1` | — | 200, 400, 401 | nie |
| GET | `/sale/matching-categories` | `categorySuggestionUsingGET` | — | 200, 401, 403, 406, 422 | nie |

## Charity

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/charity/fundraising-campaigns` | `searchFundraisingCampaigns` | — | 200, 400, 401, 403 | nie |

## Classifieds

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/classified-offers-stats` | `classifiedOffersStatsGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/sale/classified-seller-stats` | `classifiedSellerOfferStatsGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/sale/classifieds-packages` | `getClassifiedPackageConfigurationsForCategoryUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401 | nie |
| GET | `/sale/classifieds-packages/{packageId}` | `getClassifiedPackageConfigurationUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 404 | nie |
| GET | `/sale/offer-classifieds-packages/{offerId}` | `getClassifiedPackagesUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404 | nie |
| PUT | `/sale/offer-classifieds-packages/{offerId}` | `assignClassifiedPackagesUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 404, 422 | nie |

## Commission refunds

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/order/refund-claims` | `getRefundApplications` | `allegro:api:orders:read` | 200, 400, 401, 403, 406, 422 | nie |
| POST | `/order/refund-claims` | `createRefundApplication` | `allegro:api:orders:write` | 201, 400, 401, 403, 406, 422 | nie |
| DELETE | `/order/refund-claims/{claimId}` | `cancelRefundApplication` | `allegro:api:orders:write` | 204, 400, 401, 403, 404, 406, 422 | nie |
| GET | `/order/refund-claims/{claimId}` | `getRefundApplication` | `allegro:api:orders:read` | 200, 400, 401, 403, 404, 406, 422 | nie |

## Compatibility List

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/compatibility-list-suggestions` | `getCompatibilityListSuggestion` | — | 200, 400, 401, 404 | nie |
| GET | `/sale/compatibility-list/supported-categories` | `getCategoriesThatSupportCompatibilityList` | `allegro:api:sale:offers:read` | 200, 401 | nie |
| GET | `/sale/compatible-products` | `getCompatibleProducts` | `allegro:api:sale:offers:read` | 200, 304, 400, 401, 422 | nie |
| GET | `/sale/compatible-products/groups` | `getCompatibleProductsGroups` | `allegro:api:sale:offers:read` | 200, 304, 400, 401, 422 | nie |

## Contacts

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offer-contacts` | `getListOfContactsUsingGET` | `allegro:api:sale:settings:read` | 200, 400, 401, 403 | nie |
| POST | `/sale/offer-contacts` | `createContactUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 422 | nie |
| GET | `/sale/offer-contacts/{id}` | `getContactUsingGET` | `allegro:api:sale:settings:read` | 200, 400, 401, 403, 404 | nie |
| PUT | `/sale/offer-contacts/{id}` | `modifyContactUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 422 | nie |

## Conversions

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/affiliate/conversions/cps` | `getCpsConversions` | `allegro:api:affiliate:read` | 200, 400, 401, 403, 422 | nie |

## Customer returns

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/order/customer-returns` | `getCustomerReturns` | `allegro:api:orders:read` | 200, 400, 401, 403, 406 | nie |
| GET | `/order/customer-returns/{customerReturnId}` | `getCustomerReturnById` | `allegro:api:orders:read` | 200, 400, 401, 403, 404, 406 | nie |
| POST | `/order/customer-returns/{customerReturnId}/rejection` | `rejectCustomerReturnRefund` | `allegro:api:orders:write` | 200, 400, 401, 403, 406, 422 | nie |

## Delivery

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/delivery-methods` | `getListOfDeliveryMethodsUsingGET` | — | 200, 401 | nie |
| GET | `/sale/delivery-settings` | `getSaleDeliverySettings` | `allegro:api:sale:settings:read` | 200, 401, 403, 422 | nie |
| PUT | `/sale/delivery-settings` | `putSaleDeliverySettings` | `allegro:api:sale:settings:write` | 200, 401, 403, 422 | nie |
| GET | `/sale/shipping-rates` | `getListOfShippingRatestUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403 | nie |
| POST | `/sale/shipping-rates` | `createShippingRatesSetUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 422 | nie |
| GET | `/sale/shipping-rates/{id}` | `getShippingRatesSetUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/sale/shipping-rates/{id}` | `modifyShippingRatesSetUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 422 | nie |

## Deposits

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/deposit/types` | `getDepositTypes` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |

## Flexible bundles

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/flexible-bundles` | `listSellersFlexibleBundlesUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 422 | nie |
| POST | `/sale/flexible-bundles` | `createFlexibleBundleUsingPOST` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 422 | nie |
| DELETE | `/sale/flexible-bundles/{bundleId}` | `deleteFlexibleBundleUsingDELETE` | `allegro:api:sale:offers:write` | 204, 401, 404 | nie |
| GET | `/sale/flexible-bundles/{bundleId}` | `getFlexibleBundleUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 404 | nie |
| PUT | `/sale/flexible-bundles/{bundleId}` | `updateFlexibleBundleUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 422 | nie |

## Fulfillment Parcels

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/orders/{orderId}/parcels` | `getFulfillmentOrderParcels` | `allegro:api:fulfillment:read` | 200, 401, 404 | nie |

## Fulfillment Products

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/available-products` | `getAvailableProducts` | `allegro:api:fulfillment:read` | 200, 401, 403, 422 | nie |

## Fulfillment Removal

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/removal/preferences` | `getFulfillmentRemovalPreferences` | `allegro:api:fulfillment:read` | 200, 401, 403, 404 | nie |
| PUT | `/fulfillment/removal/preferences` | `createFulfillmentRemovalPreferences` | `allegro:api:fulfillment:write` | 201, 401, 403, 422 | nie |

## Fulfillment Returns

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/returns/refund-dispositions` | `getRefundDispositionsReport` | `allegro:api:fulfillment:read` | 200, 401, 403, 406, 422 | nie |

## Fulfillment Stock

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/stock` | `getFulfillmentStock` | `allegro:api:fulfillment:read` | 200, 401, 403, 422 | nie |

## Images and attachments

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| POST | `/sale/images` | `uploadOfferImageUsingPOST` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 413, 415, 422 | nie |
| POST | `/sale/offer-attachments` | `createOfferAttachmentUsingPOST` | `allegro:api:sale:offers:write` | 201, 400, 401, 415, 422 | nie |
| GET | `/sale/offer-attachments/{attachmentId}` | `getOfferAttachment` | `allegro:api:sale:offers:read` | 200, 403, 404 | nie |
| PUT | `/sale/offer-attachments/{attachmentId}` | `uploadOfferAttachmentUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 415 | nie |

## Information about marketplaces

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/marketplaces` | `marketplacesGET` | — | 200 | nie |

## Information about user

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/account/additional-emails` | `getListOfAdditionalEmailsUsingGET` | `allegro:api:profile:read` | 200, 401 | nie |
| POST | `/account/additional-emails` | `addAdditionalEmailUsingPOST` | `allegro:api:profile:write` | 201, 400, 401, 422 | nie |
| DELETE | `/account/additional-emails/{emailId}` | `deleteAdditionalEmailUsingDELETE` | `allegro:api:profile:write` | 204, 401, 404 | nie |
| GET | `/account/additional-emails/{emailId}` | `getAdditionalEmailUsingGET` | `allegro:api:profile:read` | 200, 401, 404 | nie |
| GET | `/me` | `meGET` | `allegro:api:profile:read` | 200, 401, 403 | nie |
| GET | `/sale/quality` | `getSaleQualityUsingGET` | `allegro:api:profile:read` | 200, 401, 403 | nie |
| GET | `/sale/smart` | `getSellerSmartClassificationGET` | `allegro:api:profile:read` | 200, 401, 404, 422 | nie |
| GET | `/sale/user-ratings` | `getUserRatingsUsingGET` | `allegro:api:ratings` | 200, 401, 403, 404 | nie |
| GET | `/sale/user-ratings/{ratingId}` | `getUserRatingUsingGET` | `allegro:api:ratings` | 200, 401, 403, 404 | nie |
| PUT | `/sale/user-ratings/{ratingId}/answer` | `answerUserRatingUsingPUT` | `allegro:api:ratings` | 201, 400, 401, 403, 404 | nie |
| PUT | `/sale/user-ratings/{ratingId}/removal` | `userRatingRemovalUsingPUT` | `allegro:api:ratings` | 201, 400, 401, 403, 404 | nie |

## Message Center

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| POST | `/messaging/message-attachments` | `newAttachmentDeclarationPOST` | `allegro:api:messaging` | 201, 401, 415, 422 | nie |
| GET | `/messaging/message-attachments/{attachmentId}` | `downloadAttachmentGET` | `allegro:api:messaging` | 200, 401, 404 | nie |
| PUT | `/messaging/message-attachments/{attachmentId}` | `uploadAttachmentPUT` | `allegro:api:messaging` | 200, 401, 403, 404, 413, 415 | nie |
| POST | `/messaging/messages` | `newMessagePOST` | `allegro:api:messaging` | 201, 401, 422 | nie |
| DELETE | `/messaging/messages/{messageId}` | `deleteMessageDELETE` | `allegro:api:messaging` | 204, 401, 403, 404 | tak |
| GET | `/messaging/messages/{messageId}` | `getMessageGET` | `allegro:api:messaging` | 200, 401, 404 | nie |
| GET | `/messaging/threads` | `listThreadsGET` | `allegro:api:messaging` | 200, 401, 422 | nie |
| GET | `/messaging/threads/{threadId}` | `getThreadGET` | `allegro:api:messaging` | 200, 401, 404 | nie |
| GET | `/messaging/threads/{threadId}/messages` | `listMessagesGET` | `allegro:api:messaging` | 200, 401, 403, 404, 422 | nie |
| POST | `/messaging/threads/{threadId}/messages` | `newMessageInThreadPOST` | `allegro:api:messaging` | 201, 401, 403, 404, 422 | nie |
| PUT | `/messaging/threads/{threadId}/read` | `changeReadFlagOnThreadPUT` | `allegro:api:messaging` | 200, 401, 403, 404, 422 | nie |

## Offer bundles

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/bundles` | `listSellersOfferBundlesUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 422 | tak |
| DELETE | `/sale/bundles/{bundleId}` | `deleteOfferBundleUsingGET` | `allegro:api:sale:offers:write` | 204, 401, 404 | tak |
| GET | `/sale/bundles/{bundleId}` | `getOfferBundleUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 404 | tak |
| PUT | `/sale/bundles/{bundleId}/discount` | `updateOfferBundleDiscountUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 422 | tak |

## Offer management

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| PUT | `/offers/{offerId}/change-price-commands/{commandId}` | `createChangePriceCommandUsingPUT` | `allegro:api:sale:offers:write` | 200, default | nie |
| GET | `/sale/offer-promotion-packages` | `getAvailableOfferPromotionPackages` | — | 200, 401 | nie |
| GET | `/sale/offer-publication-commands/{commandId}` | `getPublicationReportUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 403, 404 | nie |
| PUT | `/sale/offer-publication-commands/{commandId}` | `changePublicationStatusUsingPUT` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 404, 409, 422 | nie |
| GET | `/sale/offer-publication-commands/{commandId}/tasks` | `getPublicationTasksUsingGET` | `allegro:api:sale:offers:write` | 200, 401, 403, 404, 422 | nie |
| GET | `/sale/offers/promo-options` | `getPromoOptionsForSellerOffersUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 401 | nie |
| GET | `/sale/offers/promo-options-commands/{commandId}` | `getPromoModificationCommandResultUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| PUT | `/sale/offers/promo-options-commands/{commandId}` | `promoModificationCommandUsingPUT` | `allegro:api:sale:offers:write` | 201, 401, 409, 422 | nie |
| GET | `/sale/offers/promo-options-commands/{commandId}/tasks` | `getPromoModificationCommandDetailedResultUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| GET | `/sale/offers/unfilled-parameters` | `getOffersUnfilledParametersUsingGET_1` | `allegro:api:sale:offers:read` | 200, 400, 401, 403 | nie |
| DELETE | `/sale/offers/{offerId}` | `deleteOfferUsingDELETE` | `allegro:api:sale:offers:write` | 204, 401, 403, 404 | nie |
| GET | `/sale/offers/{offerId}/promo-options` | `getOfferPromoOptionsUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403 | nie |
| POST | `/sale/offers/{offerId}/promo-options-modification` | `modifyOfferPromoOptionsUsingPOST` | `allegro:api:sale:offers:write` | 200, 401, 403, 422 | nie |
| POST | `/sale/product-offers` | `createProductOffers` | `allegro:api:sale:offers:write` | 201, 202, 400, 401, 403, 422 | nie |
| PATCH | `/sale/product-offers/{offerId}` | `editProductOffers` | — | 200, 202, 400, 401, 403, 404, 409, 422 | nie |
| GET | `/sale/product-offers/{offerId}/operations/{operationId}` | `getProductOfferProcessingStatus` | `allegro:api:sale:offers:read` | 202, 303, 400, 401, 403, 404, 422 | nie |

## Offer rating

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offers/{offerId}/rating` | `offerRatingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |

## Offer tags

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offer-tags` | `listSellerTagsGET_1` | `allegro:api:sale:settings:read` | 200, 401, 403 | nie |
| POST | `/sale/offer-tags` | `createTagPOST_1` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 422 | nie |
| DELETE | `/sale/offer-tags/{tagId}` | `deleteTagUsingDELETE` | `allegro:api:sale:settings:write` | 204, 401, 403, 404 | nie |
| PUT | `/sale/offer-tags/{tagId}` | `updateTagPUT` | `allegro:api:sale:settings:write` | 200, 401, 403, 404, 422 | nie |
| GET | `/sale/offers/{offerId}/tags` | `listAssignedOfferTagsGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| POST | `/sale/offers/{offerId}/tags` | `assignTagToOfferPOST` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 404, 422 | nie |

## Offer translations

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offers/{offerId}/translations` | `getOfferTranslationUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| DELETE | `/sale/offers/{offerId}/translations/{language}` | `deleteManualTranslationUsingDELETE` | `allegro:api:sale:offers:write` | 200, 204, 401, 403 | nie |
| PATCH | `/sale/offers/{offerId}/translations/{language}` | `updateOfferTranslationUsingPATCH` | `allegro:api:sale:offers:write` | 200, 401, 403, 422 | nie |

## Order management

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/order/carriers` | `getOrdersCarriersUsingGET` | — | 200, 401, 404 | nie |
| GET | `/order/carriers/ALLEGRO/points` | `getAllegroPickupDropOffPointsGET` | — | 200, 304, 400, 401 | nie |
| GET | `/order/carriers/{carrierId}/tracking` | `getParcelTrackingUsingGET` | — | 200, 400, 401 | nie |
| GET | `/order/checkout-forms` | `getListOfOrdersUsingGET` | `allegro:api:orders:read` | 200, 400, 401, 406, 422 | nie |
| GET | `/order/checkout-forms/{id}` | `getOrdersDetailsUsingGET` | `allegro:api:orders:read` | 200, 400, 401, 404, 406, 422 | nie |
| PUT | `/order/checkout-forms/{id}/fulfillment` | `setOrderFulfillmentUsingPUT` | `allegro:api:orders:write` | 204, 401, 404, 409, 422 | nie |
| GET | `/order/checkout-forms/{id}/invoices` | `getOrderInvoicesDetails` | `allegro:api:orders:read` | 200, 403, 404 | nie |
| POST | `/order/checkout-forms/{id}/invoices` | `addOrderInvoicesMetadata` | `allegro:api:orders:write` | 201, 403, 404, 409, 422, 429 | nie |
| PUT | `/order/checkout-forms/{id}/invoices/{invoiceId}/file` | `uploadOrderInvoiceFile` | `allegro:api:orders:write` | 200, 403, 404, 409, 413, 422 | nie |
| POST | `/order/checkout-forms/{id}/serial-numbers` | `setOrderLineItemsSerialNumbersUsingPOST` | `allegro:api:orders:write` | 204, 401, 404, 409, 422 | nie |
| GET | `/order/checkout-forms/{id}/shipments` | `getOrderShipmentsUsingGET` | `allegro:api:orders:read` | 200, 401, 404 | nie |
| POST | `/order/checkout-forms/{id}/shipments` | `createOrderShipmentsUsingPOST` | `allegro:api:orders:write` | 201, 400, 401, 404, 409, 422 | nie |
| GET | `/order/event-stats` | `getOrderEventsStatisticsUsingGET` | `allegro:api:orders:read` | 200, 401 | nie |
| GET | `/order/events` | `getOrderEventsUsingGET` | `allegro:api:orders:read` | 200, 401, 403, 422 | nie |
| POST | `/order/{orderId}/billing-documents/links` | `uploadOrderBillingDocumentLink` | `allegro:api:orders:write` | 201, 403, 404, 409, 422 | nie |

## Payments

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/payments/payment-operations` | `getPaymentsOperationHistory` | `allegro:api:payments:read` | 200, 401, 422 | nie |
| GET | `/payments/refunds` | `getRefundedPayments` | `allegro:api:payments:read` | 200, 401, 403, 422 | nie |
| POST | `/payments/refunds` | `initiateRefund` | `allegro:api:payments:write` | 200, 400, 401, 403, 404, 422 | nie |

## Points of service

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/points-of-service` | `getPOSListUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 404 | nie |
| POST | `/points-of-service` | `createPOSUsingPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 404, 409, 422 | nie |
| DELETE | `/points-of-service/{id}` | `deletePOSUsingDELETE` | `allegro:api:sale:settings:write` | 204, 401, 403, 404 | nie |
| GET | `/points-of-service/{id}` | `getPOSDataUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/points-of-service/{id}` | `modifyPOSUsingPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 404, 409, 422 | nie |

## Post Purchase Issues

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/issues` | `getListOfIssuesUsingGET` | `allegro:api:disputes` | 200, 401, 404, 422 | nie |
| POST | `/sale/issues/attachments` | `createAnIssueAttachmentUsingPOST` | `allegro:api:disputes` | 201, 401, 403, 422 | nie |
| GET | `/sale/issues/attachments/{attachmentId}` | `getIssueAttachmentUsingGET` | `allegro:api:disputes` | 200, 401, 403, 404 | nie |
| PUT | `/sale/issues/attachments/{attachmentId}` | `uploadIssueAttachmentUsingPUT` | `allegro:api:disputes` | 200, 400, 401, 413, 415, 422 | nie |
| GET | `/sale/issues/{issueId}` | `getIssueUsingGET` | `allegro:api:disputes` | 200, 401, 403, 404 | nie |
| GET | `/sale/issues/{issueId}/chat` | `getChatFromIssueUsingGET` | `allegro:api:disputes` | 200, 401, 403, 404 | nie |
| POST | `/sale/issues/{issueId}/message` | `addMessageToIssueUsingPOST` | `allegro:api:disputes` | 201, 400, 401, 403, 404, 409, 422 | nie |
| POST | `/sale/issues/{issueId}/status` | `changeStatusOfIssueUsingPOST` | `allegro:api:disputes` | 200, 400, 401, 403, 404 | nie |

## Pricing

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| POST | `/pricing/offer-fee-preview` | `calculateFeePreviewUsingPOST` | `allegro:api:sale:offers:read` | 200, 400, 401, 422 | nie |
| GET | `/pricing/offer-quotes` | `offerQuotesPublicUsingGET` | `allegro:api:billing:read` | 200, 400, 401, 403, 503 | nie |

## Products

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/categories/{categoryId}/product-parameters` | `getFlatProductParametersUsingGET` | — | 200, 404 | nie |
| POST | `/sale/product-proposals` | `proposeSaleProduct` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 409, 422 | nie |
| GET | `/sale/products` | `getSaleProducts` | `allegro:api:sale:offers:read` | 200, 400, 401, 422 | nie |
| GET | `/sale/products/change-proposals/{changeProposalId}` | `getProductChangeProposal` | `allegro:api:sale:offers:read` | 200, 401, 403, 404 | nie |
| GET | `/sale/products/{productId}` | `getSaleProduct` | `allegro:api:sale:offers:read` | 200, 401, 404, 422 | nie |
| POST | `/sale/products/{productId}/change-proposals` | `productChangeProposal` | `allegro:api:sale:offers:write` | 201, 400, 401, 404, 422 | nie |

## Public user information

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/users/{userId}/ratings-summary` | `getUserSummaryUsingGET` | `allegro:api:profile:read` | 200, 401, 403, 404 | nie |

## Rebates and promotions

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/loyalty/promotions` | `listSellerPromotionsUsingGET_1` | `allegro:api:sale:offers:read` | 200, 400, 401, 422 | nie |
| POST | `/sale/loyalty/promotions` | `createPromotionUsingPOST_1` | `allegro:api:sale:offers:write` | 201, 400, 401, 403, 404, 412, 422 | nie |
| DELETE | `/sale/loyalty/promotions/{promotionId}` | `deactivatePromotionUsingDELETE` | `allegro:api:sale:offers:write` | 204, 401, 404 | nie |
| GET | `/sale/loyalty/promotions/{promotionId}` | `getPromotionUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 404 | nie |
| PUT | `/sale/loyalty/promotions/{promotionId}` | `updatePromotionUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/sale/turnover-discount` | `getTurnoverDiscountsUsingGET` | `allegro:api:sale:offers:read` | 200, 401, 403 | nie |
| PUT | `/sale/turnover-discount/{marketplaceId}` | `createOrModifyTurnoverDiscountUsingPUT` | `allegro:api:sale:offers:write` | 200, 400, 401, 403, 404, 422 | nie |
| PUT | `/sale/turnover-discount/{marketplaceId}/deactivate` | `deactivateTurnoverDiscountsUsingPUT` | `allegro:api:sale:offers:write` | 200, 204, 401, 403, 404 | nie |

## Responsible persons

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/responsible-persons` | `responsiblePersonsGET` | `allegro:api:sale:settings:read` | 200, 400, 401, 403, 422 | nie |
| POST | `/sale/responsible-persons` | `responsiblePersonsPOST` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 422 | nie |
| PUT | `/sale/responsible-persons/{id}` | `responsiblePersonsPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 422 | nie |

## Responsible producers

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/responsible-producers` | `responsibleProducersGET` | `allegro:api:sale:settings:read` | 200, 400, 401, 403, 422 | nie |
| POST | `/sale/responsible-producers` | `responsibleProducersPOST` | `allegro:api:sale:settings:write` | 201, 400, 401, 403, 422 | nie |
| GET | `/sale/responsible-producers/{id}` | `responsibleProducerGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404, 422 | nie |
| PUT | `/sale/responsible-producers/{id}` | `responsibleProducersPUT` | `allegro:api:sale:settings:write` | 200, 400, 401, 403, 422 | nie |

## Shipment management

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/shipment-management/delivery-proposals/{orderId}` | `getDeliveryProposals` | `allegro:api:shipments:write` | 200, 401, 403, 504 | nie |
| GET | `/shipment-management/delivery-services` | `getDeliveryServices` | `allegro:api:shipments:write` | 200, 401, 403, 504 | tak |
| POST | `/shipment-management/label` | `getShipmentLabels` | `allegro:api:shipments:read` | 200, 204, 400, 401, 403, 404, 504 | nie |
| POST | `/shipment-management/pickup-proposals` | `getPickupProposals` | `allegro:api:shipments:write` | 200, 400, 401, 403, 504 | nie |
| POST | `/shipment-management/pickups/create-commands` | `createPickup` | `allegro:api:shipments:write` | 200, 400, 401, 403 | nie |
| GET | `/shipment-management/pickups/create-commands/{commandId}` | `createPickupStatus` | `allegro:api:shipments:write` | 200, 400, 401, 403, 404, 504 | nie |
| GET | `/shipment-management/pickups/{pickupId}` | `getPickupDetails` | `allegro:api:shipments:read` | 200, 400, 401, 403, 404, 504 | nie |
| POST | `/shipment-management/protocol` | `getShipmentProtocol` | `allegro:api:shipments:read` | 200, 204, 400, 401, 403, 404, 504 | nie |
| POST | `/shipment-management/shipments/cancel-commands` | `cancelShipment` | `allegro:api:shipments:write` | 200, 400, 401, 403 | nie |
| GET | `/shipment-management/shipments/cancel-commands/{commandId}` | `getShipmentCancellationStatus` | `allegro:api:shipments:write` | 200, 400, 401, 403, 404, 504 | nie |
| POST | `/shipment-management/shipments/create-commands` | `createNewShipment` | `allegro:api:shipments:write` | 200, 400, 401, 403, 504 | nie |
| GET | `/shipment-management/shipments/create-commands/{commandId}` | `getShipmentCreationStatus` | `allegro:api:shipments:write` | 200, 400, 401, 403, 404, 504 | nie |
| GET | `/shipment-management/shipments/{shipmentId}` | `getShipmentDetails` | `allegro:api:shipments:read` | 200, 400, 401, 403, 404, 504 | nie |

## Size tables

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/size-tables` | `getTablesUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| POST | `/sale/size-tables` | `createTableUsingPOST` | `allegro:api:sale:settings:write` | 201, 401, 403, 404 | nie |
| GET | `/sale/size-tables-templates` | `getTablesTemplatesUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403 | nie |
| GET | `/sale/size-tables/{tableId}` | `getTableUsingGET` | `allegro:api:sale:settings:read` | 200, 401, 403, 404 | nie |
| PUT | `/sale/size-tables/{tableId}` | `modifyTableUsingPUT` | `allegro:api:sale:settings:write` | 200, 401, 403, 404 | nie |

## Tax Identification Number

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/fulfillment/tax-id` | `getTaxId` | `allegro:api:fulfillment:read` | 200, 401, 403, 404 | nie |
| POST | `/fulfillment/tax-id` | `addTaxId` | `allegro:api:fulfillment:write` | 201, 401, 403, 404, 422 | nie |
| PUT | `/fulfillment/tax-id` | `updateTaxId` | `allegro:api:fulfillment:write` | 200, 401, 403, 404, 422 | nie |

## Tax settings

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/tax-settings` | `getTaxSettingsForCategory` | — | 200, 400, 401, 403, 404, 406 | nie |

## User's offer information

| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |
|---|---|---|---|---|---|
| GET | `/sale/offer-events` | `getOfferEvents` | `allegro:api:sale:offers:read` | 200, 400, 401 | nie |
| GET | `/sale/offers` | `searchOffersUsingGET` | `allegro:api:sale:offers:read` | 200, 400, 403 | nie |
| GET | `/sale/offers/{offerId}/smart` | `getOfferSmartClassificationGET` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404, 422 | nie |
| GET | `/sale/product-offers/{offerId}` | `getProductOffer` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404 | nie |
| GET | `/sale/product-offers/{offerId}/parts` | `getPartialProductOffer` | `allegro:api:sale:offers:read` | 200, 400, 401, 403, 404 | nie |
