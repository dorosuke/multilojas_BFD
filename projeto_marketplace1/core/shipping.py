import json
import re
import unicodedata
import urllib.error
import urllib.request
from decimal import Decimal


STATE_REGIONS = {
    'AC': 'Norte',
    'AP': 'Norte',
    'AM': 'Norte',
    'PA': 'Norte',
    'RO': 'Norte',
    'RR': 'Norte',
    'TO': 'Norte',
    'AL': 'Nordeste',
    'BA': 'Nordeste',
    'CE': 'Nordeste',
    'MA': 'Nordeste',
    'PB': 'Nordeste',
    'PE': 'Nordeste',
    'PI': 'Nordeste',
    'RN': 'Nordeste',
    'SE': 'Nordeste',
    'DF': 'Centro-Oeste',
    'GO': 'Centro-Oeste',
    'MT': 'Centro-Oeste',
    'MS': 'Centro-Oeste',
    'ES': 'Sudeste',
    'MG': 'Sudeste',
    'RJ': 'Sudeste',
    'SP': 'Sudeste',
    'PR': 'Sul',
    'RS': 'Sul',
    'SC': 'Sul',
}

STATE_NAMES = {
    'ACRE': 'AC',
    'ALAGOAS': 'AL',
    'AMAPA': 'AP',
    'AMAZONAS': 'AM',
    'BAHIA': 'BA',
    'CEARA': 'CE',
    'DISTRITO FEDERAL': 'DF',
    'ESPIRITO SANTO': 'ES',
    'GOIAS': 'GO',
    'MARANHAO': 'MA',
    'MATO GROSSO': 'MT',
    'MATO GROSSO DO SUL': 'MS',
    'MINAS GERAIS': 'MG',
    'PARA': 'PA',
    'PARAIBA': 'PB',
    'PARANA': 'PR',
    'PERNAMBUCO': 'PE',
    'PIAUI': 'PI',
    'RIO DE JANEIRO': 'RJ',
    'RIO GRANDE DO NORTE': 'RN',
    'RIO GRANDE DO SUL': 'RS',
    'RONDONIA': 'RO',
    'RORAIMA': 'RR',
    'SANTA CATARINA': 'SC',
    'SAO PAULO': 'SP',
    'SERGIPE': 'SE',
    'TOCANTINS': 'TO',
}


def only_digits(value):
    return re.sub(r'\D+', '', value or '')


def normalize_text(value):
    normalized = unicodedata.normalize('NFKD', value or '')
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch))


def uf_from_text(value, fallback='SP'):
    normalized = re.sub(r'\s+', ' ', normalize_text(value).upper()).strip()
    match = re.search(r'\b([A-Z]{2})\b', normalized)
    if match and match.group(1) in STATE_REGIONS:
        return match.group(1)

    for state_name, uf in STATE_NAMES.items():
        if state_name in normalized:
            return uf
    return fallback


def fetch_cep_data(cep):
    clean_cep = only_digits(cep)
    if len(clean_cep) != 8:
        return None

    sources = [
        f'https://brasilapi.com.br/api/cep/v2/{clean_cep}',
        f'https://viacep.com.br/ws/{clean_cep}/json/',
    ]

    for url in sources:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'MultiLojas Frete Demo'})
            with urllib.request.urlopen(request, timeout=4) as response:
                payload = json.loads(response.read().decode('utf-8'))
            if payload.get('erro'):
                continue
            state = payload.get('state') or payload.get('uf')
            if state:
                return {
                    'cep': clean_cep,
                    'state': state,
                    'city': payload.get('city') or payload.get('localidade') or '',
                    'street': payload.get('street') or payload.get('logradouro') or '',
                    'source': 'BrasilAPI' if 'brasilapi' in url else 'ViaCEP',
                }
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
            continue

    return None


def calculate_shipping_quote(store, destination_postal_code, total_qty, destination_address=''):
    cep = only_digits(destination_postal_code)
    cep_data = fetch_cep_data(cep) if len(cep) == 8 else None
    destination_state = (
        (cep_data or {}).get('state')
        or uf_from_text(destination_address or destination_postal_code, fallback='SP')
    )
    origin_state = uf_from_text(
        f"{getattr(store, 'endereco_completo', '')} {getattr(store, 'cep', '')}",
        fallback='SP',
    )

    origin_region = STATE_REGIONS.get(origin_state, 'Sudeste')
    destination_region = STATE_REGIONS.get(destination_state, 'Sudeste')
    quantity = max(1, int(total_qty or 1))

    if origin_state == destination_state:
        base_value = Decimal('12.90')
        deadline_days = 3
    elif origin_region == destination_region:
        base_value = Decimal('18.90')
        deadline_days = 5
    else:
        base_value = Decimal('29.90')
        deadline_days = 8

    shipping_value = (base_value + Decimal('1.75') * Decimal(quantity)).quantize(Decimal('0.01'))

    return {
        'provider': 'brasilapi_cep_demo',
        'service': 'Entrega padrão',
        'value': shipping_value,
        'deadline_days': deadline_days,
        'origin_state': origin_state,
        'destination_state': destination_state,
        'postal_code': cep,
        'api_source': (cep_data or {}).get('source') or 'fallback_local',
        'address_hint': cep_data or {},
    }
