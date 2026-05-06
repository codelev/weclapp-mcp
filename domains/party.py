"""
Write tools for the Party API:
  • party_create  – POST  /party
  • party_update  – PUT   /party/id/{id}
  • party_delete  – DELETE /party/id/{id}
Read-only tools for the Party API:
  • party_list        – GET /party
  • party_count       – GET /party/count
  • party_get         – GET /party/id/{id}
  • party_download_image – GET /party/id/{id}/downloadImage
Action / workflow tools for the Party API:
  • party_create_public_page                  – POST /party/id/{id}/createPublicPage
  • party_transfer_addresses_to_open_records  – POST /party/id/{id}/startTransferAddressesToOpenRecords
  • party_transfer_emails_to_open_records     – POST /party/id/{id}/startTransferEmailAddressesToOpenRecords
  • party_upload_image                        – POST /party/id/{id}/uploadImage

All complex sub-objects (addresses, bankAccounts, etc.) are passed as JSON strings so the MCP parameter schema stays 
flat while preserving full API coverage.  The docstrings document exactly what each JSON array/object should contain.
"""
from __future__ import annotations
from typing import Optional
from mcp.server.fastmcp import FastMCP
from client import api_get, api_delete, api_post, api_put, parse_json_param, api_post_multipart
import base64

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_COUNTRY_CODES = (
    "AC AD AE AF AG AI AL AM AN AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG "
    "BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL "
    "CM CN CO CR CS CU CV CW CX CY CZ DE DG DJ DK DM DO DZ EA EC EE EG EH ER "
    "ES ET EU FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS "
    "GT GU GW GY HK HM HN HR HT HU IC ID IE IL IM IN IO IQ IR IS IT JE JM JO "
    "JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA "
    "MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC "
    "NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW "
    "PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST "
    "SV SX SY SZ TA TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM "
    "UNKNOWN US UY UZ VA VC VE VG VI VN VU WF WS XI XK YE YT ZA ZM ZW"
).split()

_SALUTATIONS = ["COMPANY", "FAMILY", "MR", "MRS", "NO_SALUTATION"]
_PARTY_TYPES = ["ORGANIZATION", "PERSON"]
_LEAD_STATUSES = ["CONVERTED", "DISQUALIFIED", "NEW", "PREQUALIFIED", "QUALIFIED"]
_BUSINESS_TYPES = ["B2B", "B2C", "B2G"]
_COMMISSION_TYPES = ["FIX", "FIX_AND_MARGIN", "FIX_AND_REVENUE", "MARGIN", "NO_COMMISSION", "REVENUE"]
_SATISFACTION = ["NEUTRAL", "SATISFIED", "UNSATISFIED"]
_PAYMENT_TYPES = ["ADVANCE_PAYMENT", "COUNTER_SALES", "PART_PAYMENT", "PREPAYMENT", "STANDARD"]
_ONLINE_TYPES = [
    "AMAZON", "BLOG", "EBAY", "FACEBOOK", "GOOGLE_DRIVE", "INSTAGRAM",
    "LINKEDIN", "OTHER", "PINTEREST", "SKYPE", "SLIDESHARE", "TWITTER",
    "WIKIPEDIA", "XING", "YELP", "YOUTUBE",
]


def _build_party_body(
    # ── identity
    party_type: str | None,
    salutation: str | None,
    title_id: str | None,
    first_name: str | None,
    middle_name: str | None,
    last_name: str | None,
    company: str | None,
    company2: str | None,
    person_company: str | None,
    person_department_id: str | None,
    person_role_id: str | None,
    birth_date: int | None,
    # ── contact
    email: str | None,
    email_home: str | None,
    phone: str | None,
    phone_home: str | None,
    mobile_phone1: str | None,
    mobile_phone2: str | None,
    fix_phone2: str | None,
    fax: str | None,
    website: str | None,
    # ── flags
    customer: bool | None,
    supplier: bool | None,
    sales_partner: bool | None,
    competitor: bool | None,
    # ── customer settings
    customer_number: str | None,
    customer_number_old: str | None,
    customer_business_type: str | None,
    customer_blocked: bool | None,
    customer_block_notice: str | None,
    customer_delivery_block: bool | None,
    customer_insolvent: bool | None,
    customer_insured: bool | None,
    customer_amount_insured: str | None,
    customer_credit_limit: str | None,
    customer_annual_revenue: str | None,
    customer_satisfaction: str | None,
    customer_sales_probability: int | None,
    customer_internal_note: str | None,
    customer_supplier_number: str | None,
    customer_default_header_discount: str | None,
    customer_default_header_surcharge: str | None,
    customer_sales_channel: str | None,
    customer_sales_order_payment_type: str | None,
    customer_allow_dropshipping_order_creation: bool | None,
    customer_use_customs_tariff_number: bool | None,
    customer_category_id: str | None,
    customer_payment_method_id: str | None,
    customer_term_of_payment_id: str | None,
    customer_shipment_method_id: str | None,
    customer_default_shipping_carrier_id: str | None,
    customer_default_warehouse_id: str | None,
    customer_debtor_account_id: str | None,
    customer_debtor_accounting_code_id: str | None,
    customer_non_standard_tax_id: str | None,
    customer_current_sales_stage_id: str | None,
    customer_loss_reason_id: str | None,
    customer_loss_description: str | None,
    # ── supplier settings
    supplier_number: str | None,
    supplier_number_old: str | None,
    supplier_active: bool | None,
    supplier_order_block: bool | None,
    supplier_internal_note: str | None,
    supplier_minimum_purchase_order_amount: str | None,
    supplier_customer_number_at_supplier: str | None,
    supplier_payment_method_id: str | None,
    supplier_term_of_payment_id: str | None,
    supplier_shipment_method_id: str | None,
    supplier_default_shipping_carrier_id: str | None,
    supplier_creditor_account_id: str | None,
    supplier_creditor_accounting_code_id: str | None,
    supplier_non_standard_tax_id: str | None,
    supplier_merge_items_for_ocr_invoice_upload: bool | None,
    # ── financial / tax
    tax_id: str | None,
    vat_identification_number: str | None,
    eori_number: str | None,
    currency_id: str | None,
    commercial_language_id: str | None,
    factoring: bool | None,
    purchase_via_plafond: bool | None,
    habitual_exporter: bool | None,
    # ── org
    parent_party_id: str | None,
    responsible_user_id: str | None,
    fixed_responsible_user: bool | None,
    region_id: str | None,
    sector_id: str | None,
    rating_id: str | None,
    lead_rating_id: str | None,
    lead_source_id: str | None,
    lead_status: str | None,
    company_size_id: str | None,
    legal_form_id: str | None,
    reference_number: str | None,
    description: str | None,
    # ── marketing opt-ins
    opt_in_email: bool | None,
    opt_in_letter: bool | None,
    opt_in_phone: bool | None,
    opt_in_sms: bool | None,
    # ── other flags
    enable_dropshipping_in_new_supply_sources: bool | None,
    commission_block: bool | None,
    invoice_block: bool | None,
    former_sales_partner: bool | None,
    # ── sales partner
    sales_partner_default_commission_type: str | None,
    sales_partner_default_commission_percentage: str | None,
    sales_partner_default_commission_fix: str | None,
    # ── address / email IDs
    primary_address_id: str | None,
    delivery_address_id: str | None,
    invoice_address_id: str | None,
    dunning_address_id: str | None,
    primary_contact_id: str | None,
    invoice_recipient_id: str | None,
    delivery_email_addresses_id: str | None,
    dunning_email_addresses_id: str | None,
    purchase_email_addresses_id: str | None,
    quotation_email_addresses_id: str | None,
    sales_invoice_email_addresses_id: str | None,
    sales_order_email_addresses_id: str | None,
    # ── JSON sub-entities
    addresses_json: str | None,
    bank_accounts_json: str | None,
    online_accounts_json: str | None,
    tags_json: str | None,
    topics_json: str | None,
    contacts_json: str | None,
    custom_attributes_json: str | None,
    commission_sales_partners_json: str | None,
    party_email_addresses_json: str | None,
    customer_sales_stage_history_json: str | None,
    party_habitual_exporter_letters_of_intent_json: str | None,
    # ── misc
    converted_on_date: int | None,
    x_rechnung_leitweg_id: str | None,
    image_id: str | None,
    public_page_uuid: str | None,
    public_page_expiration_date: int | None,
) -> dict:
    body: dict = {
        "partyType": party_type,
        "salutation": salutation,
        "titleId": title_id,
        "firstName": first_name,
        "middleName": middle_name,
        "lastName": last_name,
        "company": company,
        "company2": company2,
        "personCompany": person_company,
        "personDepartmentId": person_department_id,
        "personRoleId": person_role_id,
        "birthDate": birth_date,
        "email": email,
        "emailHome": email_home,
        "phone": phone,
        "phoneHome": phone_home,
        "mobilePhone1": mobile_phone1,
        "mobilePhone2": mobile_phone2,
        "fixPhone2": fix_phone2,
        "fax": fax,
        "website": website,
        "customer": customer,
        "supplier": supplier,
        "salesPartner": sales_partner,
        "competitor": competitor,
        "customerNumber": customer_number,
        "customerNumberOld": customer_number_old,
        "customerBusinessType": customer_business_type,
        "customerBlocked": customer_blocked,
        "customerBlockNotice": customer_block_notice,
        "customerDeliveryBlock": customer_delivery_block,
        "customerInsolvent": customer_insolvent,
        "customerInsured": customer_insured,
        "customerAmountInsured": customer_amount_insured,
        "customerCreditLimit": customer_credit_limit,
        "customerAnnualRevenue": customer_annual_revenue,
        "customerSatisfaction": customer_satisfaction,
        "customerSalesProbability": customer_sales_probability,
        "customerInternalNote": customer_internal_note,
        "customerSupplierNumber": customer_supplier_number,
        "customerDefaultHeaderDiscount": customer_default_header_discount,
        "customerDefaultHeaderSurcharge": customer_default_header_surcharge,
        "customerSalesChannel": customer_sales_channel,
        "customerSalesOrderPaymentType": customer_sales_order_payment_type,
        "customerAllowDropshippingOrderCreation": customer_allow_dropshipping_order_creation,
        "customerUseCustomsTariffNumber": customer_use_customs_tariff_number,
        "customerCategoryId": customer_category_id,
        "customerPaymentMethodId": customer_payment_method_id,
        "customerTermOfPaymentId": customer_term_of_payment_id,
        "customerShipmentMethodId": customer_shipment_method_id,
        "customerDefaultShippingCarrierId": customer_default_shipping_carrier_id,
        "customerDefaultWarehouseId": customer_default_warehouse_id,
        "customerDebtorAccountId": customer_debtor_account_id,
        "customerDebtorAccountingCodeId": customer_debtor_accounting_code_id,
        "customerNonStandardTaxId": customer_non_standard_tax_id,
        "customerCurrentSalesStageId": customer_current_sales_stage_id,
        "customerLossReasonId": customer_loss_reason_id,
        "customerLossDescription": customer_loss_description,
        "supplierNumber": supplier_number,
        "supplierNumberOld": supplier_number_old,
        "supplierActive": supplier_active,
        "supplierOrderBlock": supplier_order_block,
        "supplierInternalNote": supplier_internal_note,
        "supplierMinimumPurchaseOrderAmount": supplier_minimum_purchase_order_amount,
        "supplierCustomerNumberAtSupplier": supplier_customer_number_at_supplier,
        "supplierPaymentMethodId": supplier_payment_method_id,
        "supplierTermOfPaymentId": supplier_term_of_payment_id,
        "supplierShipmentMethodId": supplier_shipment_method_id,
        "supplierDefaultShippingCarrierId": supplier_default_shipping_carrier_id,
        "supplierCreditorAccountId": supplier_creditor_account_id,
        "supplierCreditorAccountingCodeId": supplier_creditor_accounting_code_id,
        "supplierNonStandardTaxId": supplier_non_standard_tax_id,
        "supplierMergeItemsForOcrInvoiceUpload": supplier_merge_items_for_ocr_invoice_upload,
        "taxId": tax_id,
        "vatIdentificationNumber": vat_identification_number,
        "eoriNumber": eori_number,
        "currencyId": currency_id,
        "commercialLanguageId": commercial_language_id,
        "factoring": factoring,
        "purchaseViaPlafond": purchase_via_plafond,
        "habitualExporter": habitual_exporter,
        "parentPartyId": parent_party_id,
        "responsibleUserId": responsible_user_id,
        "fixedResponsibleUser": fixed_responsible_user,
        "regionId": region_id,
        "sectorId": sector_id,
        "ratingId": rating_id,
        "leadRatingId": lead_rating_id,
        "leadSourceId": lead_source_id,
        "leadStatus": lead_status,
        "companySizeId": company_size_id,
        "legalFormId": legal_form_id,
        "referenceNumber": reference_number,
        "description": description,
        "optInEmail": opt_in_email,
        "optInLetter": opt_in_letter,
        "optInPhone": opt_in_phone,
        "optInSms": opt_in_sms,
        "enableDropshippingInNewSupplySources": enable_dropshipping_in_new_supply_sources,
        "commissionBlock": commission_block,
        "invoiceBlock": invoice_block,
        "formerSalesPartner": former_sales_partner,
        "salesPartnerDefaultCommissionType": sales_partner_default_commission_type,
        "salesPartnerDefaultCommissionPercentage": sales_partner_default_commission_percentage,
        "salesPartnerDefaultCommissionFix": sales_partner_default_commission_fix,
        "primaryAddressId": primary_address_id,
        "deliveryAddressId": delivery_address_id,
        "invoiceAddressId": invoice_address_id,
        "dunningAddressId": dunning_address_id,
        "primaryContactId": primary_contact_id,
        "invoiceRecipientId": invoice_recipient_id,
        "deliveryEmailAddressesId": delivery_email_addresses_id,
        "dunningEmailAddressesId": dunning_email_addresses_id,
        "purchaseEmailAddressesId": purchase_email_addresses_id,
        "quotationEmailAddressesId": quotation_email_addresses_id,
        "salesInvoiceEmailAddressesId": sales_invoice_email_addresses_id,
        "salesOrderEmailAddressesId": sales_order_email_addresses_id,
        "convertedOnDate": converted_on_date,
        "xRechnungLeitwegId": x_rechnung_leitweg_id,
        "imageId": image_id,
        "publicPageUuid": public_page_uuid,
        "publicPageExpirationDate": public_page_expiration_date,
    }
    # JSON sub-entities
    if addresses_json:
        body["addresses"] = parse_json_param(addresses_json, "addresses_json")
    if bank_accounts_json:
        body["bankAccounts"] = parse_json_param(bank_accounts_json, "bank_accounts_json")
    if online_accounts_json:
        body["onlineAccounts"] = parse_json_param(online_accounts_json, "online_accounts_json")
    if tags_json:
        body["tags"] = parse_json_param(tags_json, "tags_json")
    if topics_json:
        body["topics"] = parse_json_param(topics_json, "topics_json")
    if contacts_json:
        body["contacts"] = parse_json_param(contacts_json, "contacts_json")
    if custom_attributes_json:
        body["customAttributes"] = parse_json_param(custom_attributes_json, "custom_attributes_json")
    if commission_sales_partners_json:
        body["commissionSalesPartners"] = parse_json_param(commission_sales_partners_json, "commission_sales_partners_json")
    if party_email_addresses_json:
        body["partyEmailAddresses"] = parse_json_param(party_email_addresses_json, "party_email_addresses_json")
    if customer_sales_stage_history_json:
        body["customerSalesStageHistory"] = parse_json_param(customer_sales_stage_history_json, "customer_sales_stage_history_json")
    if party_habitual_exporter_letters_of_intent_json:
        body["partyHabitualExporterLettersOfIntent"] = parse_json_param(
            party_habitual_exporter_letters_of_intent_json, "party_habitual_exporter_letters_of_intent_json"
        )
    return body


# ---------------------------------------------------------------------------
# addresses_json schema (for docstring use)
# ---------------------------------------------------------------------------
_ADDRESSES_SCHEMA = """
addresses_json – JSON array of address objects. Each object may contain:
  id, city, company, company2, countryCode (ISO-2, e.g. "DE"),
  deliveryAddress (bool), firstName, globalLocationNumber,
  invoiceAddress (bool), lastName, phoneNumber, postOfficeBoxCity,
  postOfficeBoxNumber, postOfficeBoxZipCode, primaryAddress (bool),
  salutation ("COMPANY"|"FAMILY"|"MR"|"MRS"|"NO_SALUTATION"),
  state, street1, street2, titleId, zipcode.

Example:
  '[{"street1":"Main St 1","city":"Berlin","countryCode":"DE","primaryAddress":true}]'
"""

_BANK_ACCOUNTS_SCHEMA = """
bank_accounts_json – JSON array. Each object:
  id, accountHolder, accountNumber, bankCode, creditInstitute,
  partyId, primary (bool).

Example:
  '[{"accountHolder":"Acme GmbH","accountNumber":"DE89370400440532013000","bankCode":"37040044","creditInstitute":"Commerzbank","primary":true}]'
"""

_ONLINE_ACCOUNTS_SCHEMA = """
online_accounts_json – JSON array. Each object:
  id, accountName, accountType
  ("AMAZON"|"BLOG"|"EBAY"|"FACEBOOK"|"GOOGLE_DRIVE"|"INSTAGRAM"|
   "LINKEDIN"|"OTHER"|"PINTEREST"|"SKYPE"|"SLIDESHARE"|"TWITTER"|
   "WIKIPEDIA"|"XING"|"YELP"|"YOUTUBE"), url.

Example:
  '[{"accountType":"LINKEDIN","url":"https://linkedin.com/company/acme"}]'
"""

_CUSTOM_ATTRIBUTES_SCHEMA = """
custom_attributes_json – JSON array. Each object:
  attributeDefinitionId (required), and one value field:
  booleanValue, dateValue (timestamp ms), numberValue (decimal string),
  selectedValueId, selectedValues ([{id}]), stringValue,
  entityId, entityReferences ([{entityId, entityName}]).

Example:
  '[{"attributeDefinitionId":"abc123","stringValue":"VIP"}]'
"""

_COMMISSION_SALES_PARTNERS_SCHEMA = """
commission_sales_partners_json – JSON array. Each object:
  id, commissionFix (decimal), commissionPercentage (decimal),
  commissionType ("FIX"|"FIX_AND_MARGIN"|"FIX_AND_REVENUE"|"MARGIN"|
                  "NO_COMMISSION"|"REVENUE"),
  salesPartnerSupplierId.

Example:
  '[{"salesPartnerSupplierId":"sp-uuid","commissionType":"REVENUE","commissionPercentage":"5.00"}]'
"""

_PARTY_EMAIL_ADDRESSES_SCHEMA = """
party_email_addresses_json – JSON array. Each object:
  id, toAddresses (string), ccAddresses (string), bccAddresses (string).

Example:
  '[{"toAddresses":"billing@customer.com","ccAddresses":"finance@customer.com"}]'
"""


def register(mcp: FastMCP) -> None:
    """Register all mutation tools onto the given FastMCP instance."""

    # ------------------------------------------------------------------ #
    #  party_create                                                        #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_create(
        # ── core identity
        party_type: Optional[str] = None,
        salutation: Optional[str] = None,
        title_id: Optional[str] = None,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        company2: Optional[str] = None,
        person_company: Optional[str] = None,
        person_department_id: Optional[str] = None,
        person_role_id: Optional[str] = None,
        birth_date: Optional[int] = None,
        # ── contact info
        email: Optional[str] = None,
        email_home: Optional[str] = None,
        phone: Optional[str] = None,
        phone_home: Optional[str] = None,
        mobile_phone1: Optional[str] = None,
        mobile_phone2: Optional[str] = None,
        fix_phone2: Optional[str] = None,
        fax: Optional[str] = None,
        website: Optional[str] = None,
        # ── role flags
        customer: Optional[bool] = None,
        supplier: Optional[bool] = None,
        sales_partner: Optional[bool] = None,
        competitor: Optional[bool] = None,
        # ── customer fields
        customer_number: Optional[str] = None,
        customer_number_old: Optional[str] = None,
        customer_business_type: Optional[str] = None,
        customer_blocked: Optional[bool] = None,
        customer_block_notice: Optional[str] = None,
        customer_delivery_block: Optional[bool] = None,
        customer_insolvent: Optional[bool] = None,
        customer_insured: Optional[bool] = None,
        customer_amount_insured: Optional[str] = None,
        customer_credit_limit: Optional[str] = None,
        customer_annual_revenue: Optional[str] = None,
        customer_satisfaction: Optional[str] = None,
        customer_sales_probability: Optional[int] = None,
        customer_internal_note: Optional[str] = None,
        customer_supplier_number: Optional[str] = None,
        customer_default_header_discount: Optional[str] = None,
        customer_default_header_surcharge: Optional[str] = None,
        customer_sales_channel: Optional[str] = None,
        customer_sales_order_payment_type: Optional[str] = None,
        customer_allow_dropshipping_order_creation: Optional[bool] = None,
        customer_use_customs_tariff_number: Optional[bool] = None,
        customer_category_id: Optional[str] = None,
        customer_payment_method_id: Optional[str] = None,
        customer_term_of_payment_id: Optional[str] = None,
        customer_shipment_method_id: Optional[str] = None,
        customer_default_shipping_carrier_id: Optional[str] = None,
        customer_default_warehouse_id: Optional[str] = None,
        customer_debtor_account_id: Optional[str] = None,
        customer_debtor_accounting_code_id: Optional[str] = None,
        customer_non_standard_tax_id: Optional[str] = None,
        customer_current_sales_stage_id: Optional[str] = None,
        customer_loss_reason_id: Optional[str] = None,
        customer_loss_description: Optional[str] = None,
        # ── supplier fields
        supplier_number: Optional[str] = None,
        supplier_number_old: Optional[str] = None,
        supplier_active: Optional[bool] = None,
        supplier_order_block: Optional[bool] = None,
        supplier_internal_note: Optional[str] = None,
        supplier_minimum_purchase_order_amount: Optional[str] = None,
        supplier_customer_number_at_supplier: Optional[str] = None,
        supplier_payment_method_id: Optional[str] = None,
        supplier_term_of_payment_id: Optional[str] = None,
        supplier_shipment_method_id: Optional[str] = None,
        supplier_default_shipping_carrier_id: Optional[str] = None,
        supplier_creditor_account_id: Optional[str] = None,
        supplier_creditor_accounting_code_id: Optional[str] = None,
        supplier_non_standard_tax_id: Optional[str] = None,
        supplier_merge_items_for_ocr_invoice_upload: Optional[bool] = None,
        # ── financial / tax
        tax_id: Optional[str] = None,
        vat_identification_number: Optional[str] = None,
        eori_number: Optional[str] = None,
        currency_id: Optional[str] = None,
        commercial_language_id: Optional[str] = None,
        factoring: Optional[bool] = None,
        purchase_via_plafond: Optional[bool] = None,
        habitual_exporter: Optional[bool] = None,
        # ── org / crm
        parent_party_id: Optional[str] = None,
        responsible_user_id: Optional[str] = None,
        fixed_responsible_user: Optional[bool] = None,
        region_id: Optional[str] = None,
        sector_id: Optional[str] = None,
        rating_id: Optional[str] = None,
        lead_rating_id: Optional[str] = None,
        lead_source_id: Optional[str] = None,
        lead_status: Optional[str] = None,
        company_size_id: Optional[str] = None,
        legal_form_id: Optional[str] = None,
        reference_number: Optional[str] = None,
        description: Optional[str] = None,
        # ── marketing
        opt_in_email: Optional[bool] = None,
        opt_in_letter: Optional[bool] = None,
        opt_in_phone: Optional[bool] = None,
        opt_in_sms: Optional[bool] = None,
        # ── misc flags
        enable_dropshipping_in_new_supply_sources: Optional[bool] = None,
        commission_block: Optional[bool] = None,
        invoice_block: Optional[bool] = None,
        former_sales_partner: Optional[bool] = None,
        # ── sales partner commission defaults
        sales_partner_default_commission_type: Optional[str] = None,
        sales_partner_default_commission_percentage: Optional[str] = None,
        sales_partner_default_commission_fix: Optional[str] = None,
        # ── address / email reference IDs
        primary_address_id: Optional[str] = None,
        delivery_address_id: Optional[str] = None,
        invoice_address_id: Optional[str] = None,
        dunning_address_id: Optional[str] = None,
        primary_contact_id: Optional[str] = None,
        invoice_recipient_id: Optional[str] = None,
        delivery_email_addresses_id: Optional[str] = None,
        dunning_email_addresses_id: Optional[str] = None,
        purchase_email_addresses_id: Optional[str] = None,
        quotation_email_addresses_id: Optional[str] = None,
        sales_invoice_email_addresses_id: Optional[str] = None,
        sales_order_email_addresses_id: Optional[str] = None,
        # ── JSON sub-entities
        addresses_json: Optional[str] = None,
        bank_accounts_json: Optional[str] = None,
        online_accounts_json: Optional[str] = None,
        tags_json: Optional[str] = None,
        topics_json: Optional[str] = None,
        contacts_json: Optional[str] = None,
        custom_attributes_json: Optional[str] = None,
        commission_sales_partners_json: Optional[str] = None,
        party_email_addresses_json: Optional[str] = None,
        customer_sales_stage_history_json: Optional[str] = None,
        party_habitual_exporter_letters_of_intent_json: Optional[str] = None,
        # ── misc
        converted_on_date: Optional[int] = None,
        x_rechnung_leitweg_id: Optional[str] = None,
        image_id: Optional[str] = None,
        public_page_uuid: Optional[str] = None,
        public_page_expiration_date: Optional[int] = None,
        # ── API control
        dry_run: Optional[bool] = None,
    ) -> dict:
        """
        Create a new party (contact, customer, supplier, lead, organisation, or person).

        ── IDENTITY PARAMETERS ──────────────────────────────────────────────
        party_type : "ORGANIZATION" | "PERSON"
            Determines which fields apply (company name vs. first/last name).
        salutation : "COMPANY" | "FAMILY" | "MR" | "MRS" | "NO_SALUTATION"
        title_id : str – UUID of an existing title record (e.g. "Dr.", "Prof.")
        first_name / middle_name / last_name : str – For PERSON type.
        company / company2 : str – Primary and secondary company name (ORGANIZATION).
        person_company : str – Company name when party_type=PERSON.
        person_department_id / person_role_id : str – UUIDs for dept / role lookups.
        birth_date : int – Unix timestamp (milliseconds) of date of birth.

        ── CONTACT PARAMETERS ───────────────────────────────────────────────
        email / email_home : str – Business and private email.
        phone / phone_home / mobile_phone1 / mobile_phone2 / fix_phone2 / fax : str
        website : str

        ── ROLE FLAGS ───────────────────────────────────────────────────────
        customer / supplier / sales_partner / competitor : bool
            A party can be multiple roles simultaneously.

        ── CUSTOMER PARAMETERS ──────────────────────────────────────────────
        customer_number / customer_number_old : str
        customer_business_type : "B2B" | "B2C" | "B2G"
        customer_blocked / customer_delivery_block / customer_insolvent : bool
        customer_block_notice : str – Free-text reason for block.
        customer_insured : bool
        customer_amount_insured : str – Decimal, e.g. "50000.00"
        customer_credit_limit : str – Decimal.
        customer_annual_revenue : str – Decimal.
        customer_satisfaction : "NEUTRAL" | "SATISFIED" | "UNSATISFIED"
        customer_sales_probability : int – 0-100.
        customer_internal_note : str – HTML allowed, max 4000 chars.
        customer_supplier_number : str – This customer's number at the supplier.
        customer_default_header_discount / customer_default_header_surcharge : str – Decimal %.
        customer_sales_channel : str – e.g. "NET1", "GROSS1" (many values).
        customer_sales_order_payment_type :
            "ADVANCE_PAYMENT"|"COUNTER_SALES"|"PART_PAYMENT"|"PREPAYMENT"|"STANDARD"
        customer_allow_dropshipping_order_creation / customer_use_customs_tariff_number : bool
        customer_category_id / customer_payment_method_id / customer_term_of_payment_id : str UUIDs
        customer_shipment_method_id / customer_default_shipping_carrier_id /
        customer_default_warehouse_id : str UUIDs
        customer_debtor_account_id / customer_debtor_accounting_code_id : str UUIDs
        customer_non_standard_tax_id : str UUID
        customer_current_sales_stage_id / customer_loss_reason_id : str UUIDs
        customer_loss_description : str

        ── SUPPLIER PARAMETERS ──────────────────────────────────────────────
        supplier_number / supplier_number_old : str
        supplier_active / supplier_order_block : bool
        supplier_internal_note : str – HTML, max 1000 chars.
        supplier_minimum_purchase_order_amount : str – Decimal.
        supplier_customer_number_at_supplier : str – Max 64 chars.
        supplier_payment_method_id / supplier_term_of_payment_id /
        supplier_shipment_method_id / supplier_default_shipping_carrier_id : str UUIDs
        supplier_creditor_account_id / supplier_creditor_accounting_code_id : str UUIDs
        supplier_non_standard_tax_id : str UUID
        supplier_merge_items_for_ocr_invoice_upload : bool

        ── FINANCIAL / TAX ──────────────────────────────────────────────────
        tax_id : str – Tax registration number (max 1000).
        vat_identification_number : str – EU VAT ID (max 1000).
        eori_number : str – Economic Operators Registration and Identification.
        currency_id : str UUID
        commercial_language_id : str UUID
        factoring / purchase_via_plafond / habitual_exporter : bool

        ── ORGANISATION / CRM ───────────────────────────────────────────────
        parent_party_id : str UUID – Parent organisation.
        responsible_user_id / fixed_responsible_user : str UUID / bool
        region_id / sector_id / rating_id / lead_rating_id / lead_source_id : str UUIDs
        lead_status : "CONVERTED"|"DISQUALIFIED"|"NEW"|"PREQUALIFIED"|"QUALIFIED"
        company_size_id / legal_form_id : str UUIDs
        reference_number : str
        description : str – HTML.

        ── MARKETING OPT-INS ────────────────────────────────────────────────
        opt_in_email / opt_in_letter / opt_in_phone / opt_in_sms : bool

        ── MISC FLAGS ───────────────────────────────────────────────────────
        enable_dropshipping_in_new_supply_sources / commission_block /
        invoice_block / former_sales_partner : bool

        ── SALES PARTNER COMMISSION ─────────────────────────────────────────
        sales_partner_default_commission_type : "FIX"|"FIX_AND_MARGIN"|"FIX_AND_REVENUE"|"MARGIN"|"NO_COMMISSION"|"REVENUE"
        sales_partner_default_commission_percentage / sales_partner_default_commission_fix : str Decimal

        ── ADDRESS / EMAIL REFERENCE IDs ────────────────────────────────────
        primary_address_id / delivery_address_id / invoice_address_id /
        dunning_address_id : str UUIDs – Point to address objects in addresses_json.
        primary_contact_id / invoice_recipient_id : str UUIDs
        delivery_email_addresses_id / dunning_email_addresses_id /
        purchase_email_addresses_id / quotation_email_addresses_id /
        sales_invoice_email_addresses_id / sales_order_email_addresses_id : str UUIDs

        ── JSON SUB-ENTITIES ────────────────────────────────────────────────
        addresses_json : str
            JSON array of address objects.
            Each: {city, company, company2, countryCode, deliveryAddress,
                   firstName, globalLocationNumber, invoiceAddress, lastName,
                   phoneNumber, postOfficeBoxCity, postOfficeBoxNumber,
                   postOfficeBoxZipCode, primaryAddress,
                   salutation ("COMPANY"|"FAMILY"|"MR"|"MRS"|"NO_SALUTATION"),
                   state, street1, street2, titleId, zipcode}
            Example: '[{"street1":"Main St 1","city":"Berlin","countryCode":"DE","primaryAddress":true}]'

        bank_accounts_json : str
            JSON array. Each: {accountHolder, accountNumber, bankCode,
                               creditInstitute, partyId, primary}
            Example: '[{"accountHolder":"Acme","accountNumber":"DE89...","bankCode":"370","primary":true}]'

        online_accounts_json : str
            JSON array. Each: {accountName, accountType, url}
            accountType: "AMAZON"|"BLOG"|"EBAY"|"FACEBOOK"|"GOOGLE_DRIVE"|
                         "INSTAGRAM"|"LINKEDIN"|"OTHER"|"PINTEREST"|"SKYPE"|
                         "SLIDESHARE"|"TWITTER"|"WIKIPEDIA"|"XING"|"YELP"|"YOUTUBE"

        tags_json : str – JSON array of tag objects: '[{"id":"tag-uuid"}]'

        topics_json : str – JSON array: '[{"id":"topic-uuid"}]'

        contacts_json : str – JSON array of linked contact party IDs: '[{"id":"party-uuid"}]'

        custom_attributes_json : str
            JSON array. Each: {attributeDefinitionId, stringValue|numberValue|
                               booleanValue|dateValue|selectedValueId|
                               selectedValues|entityId|entityReferences}
            Example: '[{"attributeDefinitionId":"def-uuid","stringValue":"VIP"}]'

        commission_sales_partners_json : str
            JSON array. Each: {salesPartnerSupplierId, commissionType,
                               commissionPercentage, commissionFix}

        party_email_addresses_json : str
            JSON array. Each: {toAddresses, ccAddresses, bccAddresses}

        customer_sales_stage_history_json : str
            JSON array. Each: {salesStageId, userId}

        party_habitual_exporter_letters_of_intent_json : str
            JSON array. Each: {automaticallySuggestInInvoice, date,
                               fromSupplier, invoices:[{id}],
                               numberDeclarer (max 30), numberSupplier (max 30),
                               totalAmount (decimal), type (MULTIPLE_ACCOUNTING_EVENTS|SINGLE_ACCOUNTING_EVENT)}

        ── API CONTROL ──────────────────────────────────────────────────────
        dry_run : bool
            When True, validates the request without persisting data.
            Use this to test party creation without side effects.

        Returns
        -------
        dict  Created party record with its new 'id'.
        """
        body = _build_party_body(
            party_type=party_type, salutation=salutation, title_id=title_id,
            first_name=first_name, middle_name=middle_name, last_name=last_name,
            company=company, company2=company2, person_company=person_company,
            person_department_id=person_department_id, person_role_id=person_role_id,
            birth_date=birth_date, email=email, email_home=email_home,
            phone=phone, phone_home=phone_home, mobile_phone1=mobile_phone1,
            mobile_phone2=mobile_phone2, fix_phone2=fix_phone2, fax=fax,
            website=website, customer=customer, supplier=supplier,
            sales_partner=sales_partner, competitor=competitor,
            customer_number=customer_number, customer_number_old=customer_number_old,
            customer_business_type=customer_business_type, customer_blocked=customer_blocked,
            customer_block_notice=customer_block_notice, customer_delivery_block=customer_delivery_block,
            customer_insolvent=customer_insolvent, customer_insured=customer_insured,
            customer_amount_insured=customer_amount_insured, customer_credit_limit=customer_credit_limit,
            customer_annual_revenue=customer_annual_revenue, customer_satisfaction=customer_satisfaction,
            customer_sales_probability=customer_sales_probability, customer_internal_note=customer_internal_note,
            customer_supplier_number=customer_supplier_number,
            customer_default_header_discount=customer_default_header_discount,
            customer_default_header_surcharge=customer_default_header_surcharge,
            customer_sales_channel=customer_sales_channel,
            customer_sales_order_payment_type=customer_sales_order_payment_type,
            customer_allow_dropshipping_order_creation=customer_allow_dropshipping_order_creation,
            customer_use_customs_tariff_number=customer_use_customs_tariff_number,
            customer_category_id=customer_category_id, customer_payment_method_id=customer_payment_method_id,
            customer_term_of_payment_id=customer_term_of_payment_id,
            customer_shipment_method_id=customer_shipment_method_id,
            customer_default_shipping_carrier_id=customer_default_shipping_carrier_id,
            customer_default_warehouse_id=customer_default_warehouse_id,
            customer_debtor_account_id=customer_debtor_account_id,
            customer_debtor_accounting_code_id=customer_debtor_accounting_code_id,
            customer_non_standard_tax_id=customer_non_standard_tax_id,
            customer_current_sales_stage_id=customer_current_sales_stage_id,
            customer_loss_reason_id=customer_loss_reason_id, customer_loss_description=customer_loss_description,
            supplier_number=supplier_number, supplier_number_old=supplier_number_old,
            supplier_active=supplier_active, supplier_order_block=supplier_order_block,
            supplier_internal_note=supplier_internal_note,
            supplier_minimum_purchase_order_amount=supplier_minimum_purchase_order_amount,
            supplier_customer_number_at_supplier=supplier_customer_number_at_supplier,
            supplier_payment_method_id=supplier_payment_method_id,
            supplier_term_of_payment_id=supplier_term_of_payment_id,
            supplier_shipment_method_id=supplier_shipment_method_id,
            supplier_default_shipping_carrier_id=supplier_default_shipping_carrier_id,
            supplier_creditor_account_id=supplier_creditor_account_id,
            supplier_creditor_accounting_code_id=supplier_creditor_accounting_code_id,
            supplier_non_standard_tax_id=supplier_non_standard_tax_id,
            supplier_merge_items_for_ocr_invoice_upload=supplier_merge_items_for_ocr_invoice_upload,
            tax_id=tax_id, vat_identification_number=vat_identification_number,
            eori_number=eori_number, currency_id=currency_id,
            commercial_language_id=commercial_language_id, factoring=factoring,
            purchase_via_plafond=purchase_via_plafond, habitual_exporter=habitual_exporter,
            parent_party_id=parent_party_id, responsible_user_id=responsible_user_id,
            fixed_responsible_user=fixed_responsible_user, region_id=region_id,
            sector_id=sector_id, rating_id=rating_id, lead_rating_id=lead_rating_id,
            lead_source_id=lead_source_id, lead_status=lead_status,
            company_size_id=company_size_id, legal_form_id=legal_form_id,
            reference_number=reference_number, description=description,
            opt_in_email=opt_in_email, opt_in_letter=opt_in_letter,
            opt_in_phone=opt_in_phone, opt_in_sms=opt_in_sms,
            enable_dropshipping_in_new_supply_sources=enable_dropshipping_in_new_supply_sources,
            commission_block=commission_block, invoice_block=invoice_block,
            former_sales_partner=former_sales_partner,
            sales_partner_default_commission_type=sales_partner_default_commission_type,
            sales_partner_default_commission_percentage=sales_partner_default_commission_percentage,
            sales_partner_default_commission_fix=sales_partner_default_commission_fix,
            primary_address_id=primary_address_id, delivery_address_id=delivery_address_id,
            invoice_address_id=invoice_address_id, dunning_address_id=dunning_address_id,
            primary_contact_id=primary_contact_id, invoice_recipient_id=invoice_recipient_id,
            delivery_email_addresses_id=delivery_email_addresses_id,
            dunning_email_addresses_id=dunning_email_addresses_id,
            purchase_email_addresses_id=purchase_email_addresses_id,
            quotation_email_addresses_id=quotation_email_addresses_id,
            sales_invoice_email_addresses_id=sales_invoice_email_addresses_id,
            sales_order_email_addresses_id=sales_order_email_addresses_id,
            addresses_json=addresses_json, bank_accounts_json=bank_accounts_json,
            online_accounts_json=online_accounts_json, tags_json=tags_json,
            topics_json=topics_json, contacts_json=contacts_json,
            custom_attributes_json=custom_attributes_json,
            commission_sales_partners_json=commission_sales_partners_json,
            party_email_addresses_json=party_email_addresses_json,
            customer_sales_stage_history_json=customer_sales_stage_history_json,
            party_habitual_exporter_letters_of_intent_json=party_habitual_exporter_letters_of_intent_json,
            converted_on_date=converted_on_date, x_rechnung_leitweg_id=x_rechnung_leitweg_id,
            image_id=image_id, public_page_uuid=public_page_uuid,
            public_page_expiration_date=public_page_expiration_date,
        )
        return await api_post("/party", body=body, params={"dryRun": dry_run})

    # ------------------------------------------------------------------ #
    #  party_update                                                        #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_update(
        id: str,
        # ── core identity
        party_type: Optional[str] = None,
        salutation: Optional[str] = None,
        title_id: Optional[str] = None,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        company2: Optional[str] = None,
        person_company: Optional[str] = None,
        person_department_id: Optional[str] = None,
        person_role_id: Optional[str] = None,
        birth_date: Optional[int] = None,
        # ── contact info
        email: Optional[str] = None,
        email_home: Optional[str] = None,
        phone: Optional[str] = None,
        phone_home: Optional[str] = None,
        mobile_phone1: Optional[str] = None,
        mobile_phone2: Optional[str] = None,
        fix_phone2: Optional[str] = None,
        fax: Optional[str] = None,
        website: Optional[str] = None,
        # ── role flags
        customer: Optional[bool] = None,
        supplier: Optional[bool] = None,
        sales_partner: Optional[bool] = None,
        competitor: Optional[bool] = None,
        # ── customer fields
        customer_number: Optional[str] = None,
        customer_number_old: Optional[str] = None,
        customer_business_type: Optional[str] = None,
        customer_blocked: Optional[bool] = None,
        customer_block_notice: Optional[str] = None,
        customer_delivery_block: Optional[bool] = None,
        customer_insolvent: Optional[bool] = None,
        customer_insured: Optional[bool] = None,
        customer_amount_insured: Optional[str] = None,
        customer_credit_limit: Optional[str] = None,
        customer_annual_revenue: Optional[str] = None,
        customer_satisfaction: Optional[str] = None,
        customer_sales_probability: Optional[int] = None,
        customer_internal_note: Optional[str] = None,
        customer_supplier_number: Optional[str] = None,
        customer_default_header_discount: Optional[str] = None,
        customer_default_header_surcharge: Optional[str] = None,
        customer_sales_channel: Optional[str] = None,
        customer_sales_order_payment_type: Optional[str] = None,
        customer_allow_dropshipping_order_creation: Optional[bool] = None,
        customer_use_customs_tariff_number: Optional[bool] = None,
        customer_category_id: Optional[str] = None,
        customer_payment_method_id: Optional[str] = None,
        customer_term_of_payment_id: Optional[str] = None,
        customer_shipment_method_id: Optional[str] = None,
        customer_default_shipping_carrier_id: Optional[str] = None,
        customer_default_warehouse_id: Optional[str] = None,
        customer_debtor_account_id: Optional[str] = None,
        customer_debtor_accounting_code_id: Optional[str] = None,
        customer_non_standard_tax_id: Optional[str] = None,
        customer_current_sales_stage_id: Optional[str] = None,
        customer_loss_reason_id: Optional[str] = None,
        customer_loss_description: Optional[str] = None,
        # ── supplier fields
        supplier_number: Optional[str] = None,
        supplier_number_old: Optional[str] = None,
        supplier_active: Optional[bool] = None,
        supplier_order_block: Optional[bool] = None,
        supplier_internal_note: Optional[str] = None,
        supplier_minimum_purchase_order_amount: Optional[str] = None,
        supplier_customer_number_at_supplier: Optional[str] = None,
        supplier_payment_method_id: Optional[str] = None,
        supplier_term_of_payment_id: Optional[str] = None,
        supplier_shipment_method_id: Optional[str] = None,
        supplier_default_shipping_carrier_id: Optional[str] = None,
        supplier_creditor_account_id: Optional[str] = None,
        supplier_creditor_accounting_code_id: Optional[str] = None,
        supplier_non_standard_tax_id: Optional[str] = None,
        supplier_merge_items_for_ocr_invoice_upload: Optional[bool] = None,
        # ── financial / tax
        tax_id: Optional[str] = None,
        vat_identification_number: Optional[str] = None,
        eori_number: Optional[str] = None,
        currency_id: Optional[str] = None,
        commercial_language_id: Optional[str] = None,
        factoring: Optional[bool] = None,
        purchase_via_plafond: Optional[bool] = None,
        habitual_exporter: Optional[bool] = None,
        # ── org / crm
        parent_party_id: Optional[str] = None,
        responsible_user_id: Optional[str] = None,
        fixed_responsible_user: Optional[bool] = None,
        region_id: Optional[str] = None,
        sector_id: Optional[str] = None,
        rating_id: Optional[str] = None,
        lead_rating_id: Optional[str] = None,
        lead_source_id: Optional[str] = None,
        lead_status: Optional[str] = None,
        company_size_id: Optional[str] = None,
        legal_form_id: Optional[str] = None,
        reference_number: Optional[str] = None,
        description: Optional[str] = None,
        # ── marketing
        opt_in_email: Optional[bool] = None,
        opt_in_letter: Optional[bool] = None,
        opt_in_phone: Optional[bool] = None,
        opt_in_sms: Optional[bool] = None,
        # ── misc flags
        enable_dropshipping_in_new_supply_sources: Optional[bool] = None,
        commission_block: Optional[bool] = None,
        invoice_block: Optional[bool] = None,
        former_sales_partner: Optional[bool] = None,
        # ── sales partner commission defaults
        sales_partner_default_commission_type: Optional[str] = None,
        sales_partner_default_commission_percentage: Optional[str] = None,
        sales_partner_default_commission_fix: Optional[str] = None,
        # ── address / email reference IDs
        primary_address_id: Optional[str] = None,
        delivery_address_id: Optional[str] = None,
        invoice_address_id: Optional[str] = None,
        dunning_address_id: Optional[str] = None,
        primary_contact_id: Optional[str] = None,
        invoice_recipient_id: Optional[str] = None,
        delivery_email_addresses_id: Optional[str] = None,
        dunning_email_addresses_id: Optional[str] = None,
        purchase_email_addresses_id: Optional[str] = None,
        quotation_email_addresses_id: Optional[str] = None,
        sales_invoice_email_addresses_id: Optional[str] = None,
        sales_order_email_addresses_id: Optional[str] = None,
        # ── JSON sub-entities (full replacement on PUT)
        addresses_json: Optional[str] = None,
        bank_accounts_json: Optional[str] = None,
        online_accounts_json: Optional[str] = None,
        tags_json: Optional[str] = None,
        topics_json: Optional[str] = None,
        contacts_json: Optional[str] = None,
        custom_attributes_json: Optional[str] = None,
        commission_sales_partners_json: Optional[str] = None,
        party_email_addresses_json: Optional[str] = None,
        customer_sales_stage_history_json: Optional[str] = None,
        party_habitual_exporter_letters_of_intent_json: Optional[str] = None,
        # ── misc
        converted_on_date: Optional[int] = None,
        x_rechnung_leitweg_id: Optional[str] = None,
        image_id: Optional[str] = None,
        public_page_uuid: Optional[str] = None,
        public_page_expiration_date: Optional[int] = None,
        # ── API control
        dry_run: Optional[bool] = None,
    ) -> dict:
        """
        Update an existing party (full PUT – supply all fields you want to keep).

        Parameters
        ----------
        id : str
            Party UUID. Required. The record to update.

        All other parameters are identical to party_create.
        Important: This is a PUT (full replace), so any field omitted will
        be set to null/default on the server.  Fetch the existing record with
        party_get first, then reuse its values for fields you do not want to change.

        dry_run : bool
            Validate without persisting – useful for testing updates.

        Returns
        -------
        dict  Updated party record.
        """
        body = _build_party_body(
            party_type=party_type, salutation=salutation, title_id=title_id,
            first_name=first_name, middle_name=middle_name, last_name=last_name,
            company=company, company2=company2, person_company=person_company,
            person_department_id=person_department_id, person_role_id=person_role_id,
            birth_date=birth_date, email=email, email_home=email_home,
            phone=phone, phone_home=phone_home, mobile_phone1=mobile_phone1,
            mobile_phone2=mobile_phone2, fix_phone2=fix_phone2, fax=fax,
            website=website, customer=customer, supplier=supplier,
            sales_partner=sales_partner, competitor=competitor,
            customer_number=customer_number, customer_number_old=customer_number_old,
            customer_business_type=customer_business_type, customer_blocked=customer_blocked,
            customer_block_notice=customer_block_notice, customer_delivery_block=customer_delivery_block,
            customer_insolvent=customer_insolvent, customer_insured=customer_insured,
            customer_amount_insured=customer_amount_insured, customer_credit_limit=customer_credit_limit,
            customer_annual_revenue=customer_annual_revenue, customer_satisfaction=customer_satisfaction,
            customer_sales_probability=customer_sales_probability, customer_internal_note=customer_internal_note,
            customer_supplier_number=customer_supplier_number,
            customer_default_header_discount=customer_default_header_discount,
            customer_default_header_surcharge=customer_default_header_surcharge,
            customer_sales_channel=customer_sales_channel,
            customer_sales_order_payment_type=customer_sales_order_payment_type,
            customer_allow_dropshipping_order_creation=customer_allow_dropshipping_order_creation,
            customer_use_customs_tariff_number=customer_use_customs_tariff_number,
            customer_category_id=customer_category_id, customer_payment_method_id=customer_payment_method_id,
            customer_term_of_payment_id=customer_term_of_payment_id,
            customer_shipment_method_id=customer_shipment_method_id,
            customer_default_shipping_carrier_id=customer_default_shipping_carrier_id,
            customer_default_warehouse_id=customer_default_warehouse_id,
            customer_debtor_account_id=customer_debtor_account_id,
            customer_debtor_accounting_code_id=customer_debtor_accounting_code_id,
            customer_non_standard_tax_id=customer_non_standard_tax_id,
            customer_current_sales_stage_id=customer_current_sales_stage_id,
            customer_loss_reason_id=customer_loss_reason_id, customer_loss_description=customer_loss_description,
            supplier_number=supplier_number, supplier_number_old=supplier_number_old,
            supplier_active=supplier_active, supplier_order_block=supplier_order_block,
            supplier_internal_note=supplier_internal_note,
            supplier_minimum_purchase_order_amount=supplier_minimum_purchase_order_amount,
            supplier_customer_number_at_supplier=supplier_customer_number_at_supplier,
            supplier_payment_method_id=supplier_payment_method_id,
            supplier_term_of_payment_id=supplier_term_of_payment_id,
            supplier_shipment_method_id=supplier_shipment_method_id,
            supplier_default_shipping_carrier_id=supplier_default_shipping_carrier_id,
            supplier_creditor_account_id=supplier_creditor_account_id,
            supplier_creditor_accounting_code_id=supplier_creditor_accounting_code_id,
            supplier_non_standard_tax_id=supplier_non_standard_tax_id,
            supplier_merge_items_for_ocr_invoice_upload=supplier_merge_items_for_ocr_invoice_upload,
            tax_id=tax_id, vat_identification_number=vat_identification_number,
            eori_number=eori_number, currency_id=currency_id,
            commercial_language_id=commercial_language_id, factoring=factoring,
            purchase_via_plafond=purchase_via_plafond, habitual_exporter=habitual_exporter,
            parent_party_id=parent_party_id, responsible_user_id=responsible_user_id,
            fixed_responsible_user=fixed_responsible_user, region_id=region_id,
            sector_id=sector_id, rating_id=rating_id, lead_rating_id=lead_rating_id,
            lead_source_id=lead_source_id, lead_status=lead_status,
            company_size_id=company_size_id, legal_form_id=legal_form_id,
            reference_number=reference_number, description=description,
            opt_in_email=opt_in_email, opt_in_letter=opt_in_letter,
            opt_in_phone=opt_in_phone, opt_in_sms=opt_in_sms,
            enable_dropshipping_in_new_supply_sources=enable_dropshipping_in_new_supply_sources,
            commission_block=commission_block, invoice_block=invoice_block,
            former_sales_partner=former_sales_partner,
            sales_partner_default_commission_type=sales_partner_default_commission_type,
            sales_partner_default_commission_percentage=sales_partner_default_commission_percentage,
            sales_partner_default_commission_fix=sales_partner_default_commission_fix,
            primary_address_id=primary_address_id, delivery_address_id=delivery_address_id,
            invoice_address_id=invoice_address_id, dunning_address_id=dunning_address_id,
            primary_contact_id=primary_contact_id, invoice_recipient_id=invoice_recipient_id,
            delivery_email_addresses_id=delivery_email_addresses_id,
            dunning_email_addresses_id=dunning_email_addresses_id,
            purchase_email_addresses_id=purchase_email_addresses_id,
            quotation_email_addresses_id=quotation_email_addresses_id,
            sales_invoice_email_addresses_id=sales_invoice_email_addresses_id,
            sales_order_email_addresses_id=sales_order_email_addresses_id,
            addresses_json=addresses_json, bank_accounts_json=bank_accounts_json,
            online_accounts_json=online_accounts_json, tags_json=tags_json,
            topics_json=topics_json, contacts_json=contacts_json,
            custom_attributes_json=custom_attributes_json,
            commission_sales_partners_json=commission_sales_partners_json,
            party_email_addresses_json=party_email_addresses_json,
            customer_sales_stage_history_json=customer_sales_stage_history_json,
            party_habitual_exporter_letters_of_intent_json=party_habitual_exporter_letters_of_intent_json,
            converted_on_date=converted_on_date, x_rechnung_leitweg_id=x_rechnung_leitweg_id,
            image_id=image_id, public_page_uuid=public_page_uuid,
            public_page_expiration_date=public_page_expiration_date,
        )
        return await api_put(f"/party/id/{id}", body=body, params={"dryRun": dry_run})

    # ------------------------------------------------------------------ #
    #  party_delete                                                        #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_delete(id: str, dry_run: Optional[bool] = None) -> dict:
        """
        Permanently delete a party by its ID.

        ⚠️  This action is irreversible unless dry_run=True.

        Parameters
        ----------
        id : str
            Party UUID. Required. The record to delete.
        dry_run : bool, optional
            When True, checks whether the delete would succeed without
            actually removing the record.  Use this to confirm safety
            before executing a real delete.

        Returns
        -------
        dict  Confirmation of deletion or dry-run result.
        """
        return await api_delete(f"/party/id/{id}", params={"dryRun": dry_run})

    # ------------------------------------------------------------------ #
    #  party_list                                                          #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_list(
            filter: Optional[str] = None,
            sort: Optional[str] = None,
            page: Optional[int] = None,
            page_size: Optional[int] = None,
            offset: Optional[int] = None,
            properties: Optional[str] = None,
            include_referenced_entities: Optional[str] = None,
            additional_properties: Optional[str] = None,
            serialize_nulls: Optional[bool] = None,
    ) -> dict:
        """
        Query / search for parties (contacts, customers, suppliers, leads, organisations, persons).

        Parameters
        ----------
        filter : str, optional
            Filter expression in the platform's filter language.
            Examples:
              • "customer = true"
              • "lastName like '%Smith%'"
              • "createdDate > 1700000000000"
              • "supplier = true AND countryCode = 'DE'"
        sort : str, optional
            Sort expression. Examples: "lastName ASC", "createdDate DESC".
        page : int, optional
            Page number (1-based) for paginated results.
        page_size : int, optional
            Number of records per page.
        offset : int, optional
            Raw offset (alternative to page/page_size).
        properties : str, optional
            Comma-separated list of properties to return (projection).
            Example: "id,firstName,lastName,email,customer"
        include_referenced_entities : str, optional
            Comma-separated entity types to embed inline.
            Example: "addresses,bankAccounts"
        additional_properties : str, optional
            Additional property keys to include in the response.
        serialize_nulls : bool, optional
            When True, null fields are included in the response JSON.

        Returns
        -------
        dict  API response with matching party records under data.
        """
        return await api_get(
            "/party",
            {
                "filter": filter,
                "sort": sort,
                "page": page,
                "pageSize": page_size,
                "offset": offset,
                "properties": properties,
                "includeReferencedEntities": include_referenced_entities,
                "additionalProperties": additional_properties,
                "serializeNulls": serialize_nulls,
            },
        )

    # ------------------------------------------------------------------ #
    #  party_count                                                         #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_count(filter: Optional[str] = None) -> dict:
        """
        Count parties matching an optional filter.

        Parameters
        ----------
        filter : str, optional
            Filter expression. Same syntax as party_list.
            Examples:
              • "customer = true"
              • "supplier = true AND countryCode = 'DE'"
              • "createdDate > 1700000000000"

        Returns
        -------
        dict  {"success": true, "data": <count as integer>}
        """
        return await api_get("/party/count", {"filter": filter})

    # ------------------------------------------------------------------ #
    #  party_get                                                           #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_get(id: str) -> dict:
        """
        Retrieve a single party record by its unique ID.

        Parameters
        ----------
        id : str
            The party's unique identifier (UUID). Required.

        Returns
        -------
        dict  Full party record including all sub-entities.
        """
        return await api_get(f"/party/id/{id}")

    # ------------------------------------------------------------------ #
    #  party_download_image                                                #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_download_image(
            id: str,
            image_id: Optional[str] = None,
            scale_width: Optional[int] = None,
            scale_height: Optional[int] = None,
    ) -> dict:
        """
        Download (or get a link to) the profile image of a party.

        Parameters
        ----------
        id : str
            Party UUID. Required.
        image_id : str, optional
            Specific image ID to download (if the party has multiple images).
        scale_width : int, optional
            Scale the returned image to this width in pixels.
        scale_height : int, optional
            Scale the returned image to this height in pixels.

        Returns
        -------
        dict  Response body with image data or URL.
        """
        return await api_get(
            f"/party/id/{id}/downloadImage",
            {
                "imageId": image_id,
                "scaleWidth": scale_width,
                "scaleHeight": scale_height,
            },
        )
    # ------------------------------------------------------------------ #
    #  party_create_public_page                                            #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_create_public_page(id: str) -> dict:
        """
        Generate a publicly accessible page for a party record.

        The API will set publicPageUuid and publicPageExpirationDate on the party.
        The returned URL can be shared externally without requiring a login.

        Parameters
        ----------
        id : str
            Party UUID. Required.

        Returns
        -------
        dict  Response including the public page URL or UUID.
        """
        return await api_post(f"/party/id/{id}/createPublicPage")

    # ------------------------------------------------------------------ #
    #  party_transfer_addresses_to_open_records                           #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_transfer_addresses_to_open_records(
            id: str,
            address_id: Optional[str] = None,
    ) -> dict:
        """
        Trigger a background job that propagates address changes on this
        party to all open (unfinished) documents that reference it —
        such as open sales orders, purchase orders, invoices, or quotations.

        Use this after updating a party's address when you need those
        changes reflected on existing open records immediately.

        Parameters
        ----------
        id : str
            Party UUID. Required.
        address_id : str, optional
            UUID of the specific address to transfer. When omitted,
            the party's primary address is used.

        Returns
        -------
        dict  Job confirmation / async task reference.
        """
        return await api_post(
            f"/party/id/{id}/startTransferAddressesToOpenRecords",
            params={"addressId": address_id},
        )

    # ------------------------------------------------------------------ #
    #  party_transfer_emails_to_open_records                              #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_transfer_emails_to_open_records(
            id: str,
            party_email_address_id: Optional[str] = None,
    ) -> dict:
        """
        Trigger a background job that propagates email address changes on
        this party to all open documents that reference it — so that
        existing open records receive the updated email addresses.

        Parameters
        ----------
        id : str
            Party UUID. Required.
        party_email_address_id : str, optional
            UUID of the specific partyEmailAddress object to transfer.
            When omitted, the party's default email addresses are used.

        Returns
        -------
        dict  Job confirmation / async task reference.
        """
        return await api_post(
            f"/party/id/{id}/startTransferEmailAddressesToOpenRecords",
            params={"partyEmailAddressId": party_email_address_id},
        )

    # ------------------------------------------------------------------ #
    #  party_upload_image                                                  #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def party_upload_image(
            id: str,
            image_base64: str,
            filename: Optional[str] = "image.jpg",
    ) -> dict:
        """
        Upload a profile image for a party.

        The image is supplied as a base64-encoded string (the MCP transport
        does not support raw binary).  The server stores the image and sets
        the 'imageId' field on the party record.

        Parameters
        ----------
        id : str
            Party UUID. Required.
        image_base64 : str
            Base64-encoded image data (JPEG, PNG, or GIF recommended).
            Do NOT include the "data:image/...;base64," prefix –
            pass only the raw base64 payload.

            To encode a file in Python:
              import base64
              data = base64.b64encode(open("photo.jpg","rb").read()).decode()

            To encode in shell:
              base64 -w0 photo.jpg

        filename : str, optional
            Original filename with extension (e.g. "profile.jpg").
            Helps the server detect the MIME type. Defaults to "image.jpg".

        Returns
        -------
        dict  Response containing the new imageId assigned to the party.

        Raises
        ------
        ValueError  If image_base64 is not valid base64.
        """
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as exc:
            raise ValueError(
                "image_base64 is not valid base64. "
                "Encode your image file with base64.b64encode(data).decode() "
                f"before passing it here. Error: {exc}"
            ) from exc

        return await api_post_multipart(
            f"/party/id/{id}/uploadImage",
            file_bytes=image_bytes,
            filename=filename or "image.jpg",
        )

    # Register resources
    @mcp.resource("party://{id}")
    async def get_party_resource(id: str) -> dict:
        """Get a party by ID as a resource."""
        from client import api_get
        return await api_get(f"/party/id/{id}")
