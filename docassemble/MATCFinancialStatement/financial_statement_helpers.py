import re

from docassemble.base.util import currency, defined, log, set_variables, value

__names__ = [
    "financial_statement_other_user",
    "_fs_elements",
    "_fs_item_total",
    "_fs_item_matches_source",
    "_fs_item_description",
    "_fs_list_prefixes",
    "_fs_prefixed_total",
    "_fs_prefixed_descriptions",
    "_income_weekly",
    "_income_descriptions",
    "_to_weekly_safe",
    "_short_expense_weekly",
    "fs_expense_descriptions",
    "_long_expense_weekly",
    "_schedule_a_expense_monthly",
    "_schedule_a_expense_descriptions",
    "_schedule_b_expense_annual",
    "_schedule_b_expense_descriptions",
    "fs_log",
    "to_weekly",
    "cadence_to_times_per_year",
    "fs_safe_float",
    "fs_currency_zero",
    "fs_text_or_default",
    "fs_showifdef_or_default",
    "fs_normalize_phone",
    "fs_item_value",
    "fs_sum_list_attr",
    "_other_assets_total_by_type",
    "_other_asset_items_by_type",
    "_other_asset_nth_attr",
    "_short_asset_group_items",
    "_short_asset_nth_attr",
    "fs_yes_no_text",
    "fs_vehicle_label",
    "fs_pension_label",
    "fs_other_asset_label",
    "fs_liability_label",
]

__all__ = __names__


def _current_user():
    return value("users[i]")


def _current_user_attr(attr_name):
    return value(f"users[i].{attr_name}")


def financial_statement_other_user(statement_user):
    users = value("users")
    for user in users:
        if user is not statement_user:
            return user
    return users[1] if statement_user is users[0] else users[0]


def _fs_elements(items):
    elements = getattr(items, "elements", items)
    return elements.values() if isinstance(elements, dict) else elements


def _fs_item_total(item, times_per_year):
    try:
        return item.total(times_per_year=times_per_year) if hasattr(item, "total") else 0
    except Exception:
        item_value = fs_item_value(item, "value")
        if item_value in (None, ""):
            return 0
        item_times_per_year = fs_item_value(item, "times_per_year")
        if item_times_per_year in (None, ""):
            item_times_per_year = times_per_year
        return fs_safe_float(item_value) * fs_safe_float(item_times_per_year) / times_per_year


def _fs_item_matches_source(item, source_key):
    return fs_text_or_default(fs_item_value(item, "source")) == source_key


def _fs_item_description(item):
    return fs_text_or_default(fs_item_value(item, "description"))


def _fs_list_prefixes(list_name, max_items=100):
    for index in range(max_items):
        prefix = f"{list_name}[{index}]"
        if defined(f"{prefix}.source"):
            yield prefix


def _fs_prefixed_total(list_name, source_key, times_per_year):
    total = 0
    for prefix in _fs_list_prefixes(list_name):
        if fs_text_or_default(value(f"{prefix}.source")) == source_key:
            item_value = value(f"{prefix}.value") if defined(f"{prefix}.value") else 0
            item_times_per_year = (
                value(f"{prefix}.times_per_year")
                if defined(f"{prefix}.times_per_year")
                else times_per_year
            )
            total += fs_safe_float(item_value) * fs_safe_float(item_times_per_year) / times_per_year
    return total


def _fs_prefixed_descriptions(list_name, source_key):
    descriptions = []
    for prefix in _fs_list_prefixes(list_name):
        if fs_text_or_default(value(f"{prefix}.source")) == source_key:
            description = fs_text_or_default(
                value(f"{prefix}.description") if defined(f"{prefix}.description") else ""
            )
            if description:
                descriptions.append(description)
    return "; ".join(descriptions)


def _income_weekly(source_key):
    try:
        return _current_user_attr("income_list").total(times_per_year=52, source=source_key)
    except Exception:
        return 0


def _income_descriptions(source_key):
    try:
        descriptions = []
        for item in _current_user_attr("income_list").matches(source_key):
            description = fs_text_or_default(item.description if hasattr(item, "description") else "")
            if description:
                descriptions.append(description)
    except Exception:
        return ""
    return "; ".join(descriptions)


def _to_weekly_safe(var_name):
    try:
        amount = value(var_name) if defined(var_name) else 0
        cadence = _current_user_attr("financial_cadence_default")
        return to_weekly(amount, cadence) if amount else 0
    except Exception:
        return 0


def _short_expense_weekly(source_key):
    try:
        return _current_user_attr("expense_list").total(times_per_year=52, source=source_key)
    except Exception:
        return 0


def fs_expense_descriptions(items, source_key):
    try:
        descriptions = []
        for item in items:
            if fs_item_value(item, "source") != source_key:
                continue
            description = fs_text_or_default(fs_item_value(item, "description"))
            if description:
                descriptions.append(description)
    except Exception:
        return ""
    return "; ".join(descriptions)


def _long_expense_weekly(source_key):
    try:
        return _current_user_attr("long_expense_list").total(times_per_year=52, source=source_key)
    except Exception:
        return 0


def _schedule_a_expense_monthly(source_key):
    try:
        return _current_user_attr("schedule_a_expenses").total(times_per_year=12, source=source_key)
    except Exception:
        return 0


def _schedule_a_expense_descriptions(source_key):
    try:
        descriptions = []
        for item in _current_user_attr("schedule_a_expenses").matches(source_key):
            description = fs_text_or_default(item.description if hasattr(item, "description") else "")
            if description:
                descriptions.append(description)
    except Exception:
        return ""
    return "; ".join(descriptions)


def _schedule_b_expense_annual(source_key):
    try:
        return _current_user_attr("schedule_b_expenses").total(times_per_year=1, source=source_key)
    except Exception:
        return 0


def _schedule_b_expense_descriptions(source_key):
    try:
        descriptions = []
        for item in _current_user_attr("schedule_b_expenses").matches(source_key):
            description = fs_text_or_default(item.description if hasattr(item, "description") else "")
            if description:
                descriptions.append(description)
    except Exception:
        return ""
    return "; ".join(descriptions)


def fs_log(message, level="debug"):
    log(f"[fs] {message}", level)
    if not defined("debug_log"):
        set_variables({"debug_log": []})
    value("debug_log").append(message)


def to_weekly(amount, cadence):
    if amount is None:
        return 0
    try:
        weekly_value = float(amount)
    except Exception:
        return 0
    if cadence == "weekly":
        return weekly_value
    if cadence == "biweekly":
        return weekly_value / 2
    if cadence == "semimonthly":
        return weekly_value / 2.15
    if cadence == "monthly":
        return weekly_value / 4.3
    if cadence == "annual":
        return weekly_value / 52
    return weekly_value


def cadence_to_times_per_year(cadence):
    if cadence == "weekly":
        return 52
    if cadence == "biweekly":
        return 26
    if cadence == "semimonthly":
        return 24
    if cadence == "monthly":
        return 12
    if cadence == "annual":
        return 1
    return 52


def fs_safe_float(amount):
    try:
        return float(amount)
    except Exception:
        return 0.0


def fs_currency_zero(amount):
    if amount in (None, ""):
        return currency(0)
    return currency(fs_safe_float(amount))


def fs_text_or_default(text, default=""):
    if text is None:
        return default
    text = str(text).strip()
    return text if text else default


def fs_showifdef_or_default(var_name, default=""):
    if defined(var_name):
        return fs_text_or_default(value(var_name), default)
    return default


def fs_normalize_phone(phone):
    if phone in (None, ""):
        return ""
    raw = str(phone).strip()
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
    return raw


def fs_item_value(item, attr_name):
    var_name = f"{item.instanceName}.{attr_name}"
    if defined(var_name):
        return value(var_name)
    return None


def fs_sum_list_attr(items, attr_name):
    total = 0.0
    try:
        for item in items:
            item_value = fs_item_value(item, attr_name)
            if item_value not in (None, ""):
                total += fs_safe_float(item_value)
    except Exception:
        return 0.0
    return total


def _other_assets_total_by_type(asset_type_key):
    total = 0.0
    try:
        for item in _current_user_attr("other_assets"):
            if fs_item_value(item, "asset_type") == asset_type_key:
                item_value = fs_item_value(item, "current_balance")
                if item_value not in (None, ""):
                    total += fs_safe_float(item_value)
    except Exception:
        return 0.0
    return total


def _other_asset_items_by_type(asset_type_key):
    matches = []
    try:
        for item in _current_user_attr("other_assets"):
            if fs_item_value(item, "asset_type") == asset_type_key:
                matches.append(item)
    except Exception:
        return []
    return matches


def _other_asset_nth_attr(asset_type_key, index, attr_name):
    matches = _other_asset_items_by_type(asset_type_key)
    if len(matches) > index:
        return fs_text_or_default(fs_item_value(matches[index], attr_name))
    return ""


def _short_asset_group_items(group_name):
    account_types = {
        "checking",
        "savings",
        "cash",
        "cd",
        "credit_union",
        "escrow",
        "stocks",
        "bonds",
        "bond_funds",
        "notes_held",
        "brokerage_cash",
        "money_market",
        "us_savings_bonds",
        "ira",
        "keough",
        "profit_sharing",
        "deferred_comp",
        "other_retirement",
    }
    excluded_types = {"annuity", "life_insurance_cash"}
    grouped_items = []
    try:
        for item in _current_user_attr("other_assets"):
            asset_type = fs_item_value(item, "asset_type")
            if group_name == "account" and asset_type in account_types:
                grouped_items.append(item)
            elif (
                group_name == "other"
                and asset_type not in account_types
                and asset_type not in excluded_types
            ):
                grouped_items.append(item)
    except Exception:
        return []
    return grouped_items


def _short_asset_nth_attr(group_name, index, attr_name):
    grouped_items = _short_asset_group_items(group_name)
    if len(grouped_items) > index:
        return fs_text_or_default(fs_item_value(grouped_items[index], attr_name))
    return ""


def fs_yes_no_text(var_name):
    if not defined(var_name):
        return "Not answered"
    return "Yes" if bool(value(var_name)) else "No"


def fs_vehicle_label(item):
    parts = []
    for attr_name in ("purchase_year", "make", "model", "vehicle_type"):
        item_value = fs_item_value(item, attr_name)
        if item_value not in (None, ""):
            parts.append(str(item_value))
    if parts:
        return " ".join(parts)
    return "Vehicle"


def fs_pension_label(item):
    institution = fs_text_or_default(fs_item_value(item, "institution"))
    if institution:
        return institution
    account_number = fs_text_or_default(fs_item_value(item, "account_number"))
    if account_number:
        return f"Retirement plan {account_number}"
    return "Retirement plan"


def fs_other_asset_label(item):
    asset_type = fs_text_or_default(fs_item_value(item, "asset_type"))
    if defined("other_asset_type_choices"):
        asset_type_label = dict(value("other_asset_type_choices")).get(asset_type, asset_type)
    else:
        asset_type_label = asset_type
    description = fs_text_or_default(fs_item_value(item, "description"))
    institution = fs_text_or_default(fs_item_value(item, "institution"))
    if description:
        return description
    if institution:
        return institution
    if asset_type_label:
        return asset_type_label
    return "Asset"


def fs_liability_label(item):
    creditor = fs_text_or_default(fs_item_value(item, "creditor"))
    debt_type = fs_text_or_default(fs_item_value(item, "debt_type"))
    if creditor and debt_type:
        return f"{creditor} ({debt_type})"
    if creditor:
        return creditor
    if debt_type:
        return debt_type
    return "Liability"
