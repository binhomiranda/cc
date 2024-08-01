import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configuração do webhook default
DEFAULT_WEBHOOK_URL = 'https://hook.us1.make.com/substitua-pelo-hook'  # Substitua pela URL do seu webhook default

# Função para enviar dados simulados com payload completo
def send_test_data(event_name, buyer_info, webhook_url):
    payload = {
        "Id": "ba832fe9-4c45-47a0-a32b-e91d0ab1e37c",
        "IsTest": True,
        "Event": event_name,
        "CreatedAt": datetime.now().isoformat(),
        "Data": {
            "Products": [
                {
                    "Id": "ed4bf7d8-5928-4bd8-b87c-c752c74f9fc2",
                    "Name": "TheBossPagamentoUnico"
                }
            ],
            "Buyer": {
                "Id": "1ee5adbb-8096-4619-81cf-90e2fcf37538",
                "Email": buyer_info["email"],
                "Name": buyer_info["name"],
                "PhoneNumber": buyer_info["phonenumber"],
                "Document": "663.614.400-95",
                "Address": {
                    "ZipCode": "15056-131",
                    "Street": "Rua Mariana Pereira Butinhon",
                    "StreetNumber": "1",
                    "Complement": "Complemento",
                    "District": "Village Damha Rio Preto III",
                    "City": "São Paulo",
                    "State": "São Paulo"
                }
            },
            "Seller": {
                "Id": "e410241c-06f9-43f8-819d-8aa65f311ec8",
                "Email": "enrico.alvarenga@lastlink.com"
            },
            "Purchase": {
                "PaymentId": "9e430c87-0522-477b-8d5e-ce69501983bd",
                "Recurrency": 3,
                "PaymentDate": datetime.now().isoformat(),
                "OriginalPrice": {
                    "Value": 12.5
                },
                "Price": {
                    "Value": 12.5
                },
                "Payment": {
                    "NumberOfInstallments": 1,
                    "PaymentMethod": "credit_card"
                },
                "Affiliate": {
                    "Id": "2d54a189-5f4f-4012-9135-6a7b870e2e72",
                    "Email": "test.affiliate@mail.com"
                }
            },
            "Subscriptions": [
                {
                    "Id": "573373d9-d62c-4895-9b74-87f0579c7038",
                    "ProductId": "ed4bf7d8-5928-4bd8-b87c-c752c74f9fc2"
                }
            ]
        }
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        st.success(f"Success: {event_name} - {response.status_code}")
        return {"event": event_name, "status": "Success", "response_code": response.status_code, "timestamp": datetime.now(), "payload": payload}
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {event_name} - {e}")
        return {"event": event_name, "status": "Error", "error": str(e), "timestamp": datetime.now(), "payload": payload}

# Função para testar eventos selecionados
def test_selected_events(selected_events, buyer_info, webhook_url):
    results = []
    for event in selected_events:
        st.write(f"Sending event: {event} with buyer info: {buyer_info} to {webhook_url}")
        result = send_test_data(event, buyer_info, webhook_url)
        results.append(result)
        time.sleep(1)  # Intervalo entre as requisições
    return results

# Interface Streamlit
st.title("Make Flow Testing Dashboard - CC")

# Entrada do webhook URL
st.write("Enter the webhook URL or select to use the default:")
use_default_webhook = st.checkbox("Use Default Webhook URL", value=False)
webhook_url = st.text_input("Webhook URL", DEFAULT_WEBHOOK_URL if use_default_webhook else "")

# Entrada de informações do comprador
st.write("Preencha com os dados simulados de um comprador (deixando sem preencher, o sistema emula um usuário):")
buyer_name = st.text_input("Name", "")
buyer_email = st.text_input("Email", "")
buyer_phonenumber = st.text_input("Phone Number", "")

buyer_info = {
    "name": buyer_name if buyer_name else "maises pereira",
    "email": buyer_email if buyer_email else "test.email@mail.com",
    "phonenumber": buyer_phonenumber if buyer_phonenumber else "+5500987645312"
}

# Seleção de eventos
st.write("Select the events you want to test:")
events = [
    "Subscription_Canceled",
    "Payment_Chargeback",
    "Recurrent_Payment",
    "Subscription_Renewal_Pending",
    "Purchase_Request_Expired",
    "Product_access_ended"
]
selected_events = st.multiselect("Events", events)

# Botão para enviar eventos selecionados
if st.button("Send Selected Events"):
    if selected_events and webhook_url:
        st.write("Sending selected events...")
        test_results = test_selected_events(selected_events, buyer_info, webhook_url)
        st.write("Selected events sent.")
        st.write(test_results)
    else:
        st.warning("Please select at least one event and enter a valid webhook URL.")

# Botão para enviar todos os eventos
if st.button("Send All Events"):
    if webhook_url:
        st.write("Sending all events...")
        test_results = test_selected_events(events, buyer_info, webhook_url)
        st.write("All events sent.")
        st.write(test_results)
    else:
        st.warning("Please enter a valid webhook URL.")

# Mostrar logs dos testes
if 'test_log' not in st.session_state:
    st.session_state.test_log = []

if 'test_results' in locals():
    st.session_state.test_log.extend(test_results)

st.write("Test Log")
for log in st.session_state.test_log:
    st.write(f"Event: {log['event']}, Status: {log['status']}, Timestamp: {log['timestamp']}")
    st.json(log['payload'])  # Mostrar payload enviado
    if log['status'] == "Error":
        st.error(log['error'])

# Adicionar tabela de eventos com descrição
st.write("## Eventos e Descrições")

event_descriptions = {
    "Subscription_Canceled": "O evento ocorre quando uma assinatura é cancelada.",
    "Payment_Chargeback": "O evento ocorre quando um pagamento sofre um chargeback.",
    "Recurrent_Payment": "O evento ocorre quando um pagamento recorrente é realizado.",
    "Subscription_Renewal_Pending": "O evento ocorre quando uma renovação de assinatura está pendente.",
    "Purchase_Request_Expired": "O evento ocorre quando uma solicitação de compra expira.",
    "Product_access_ended": "O evento ocorre quando o acesso a um produto termina."
}

event_data = [{"Event": event, "Description": description} for event, description in event_descriptions.items() if event in events]

st.table(event_data)

st.write("Para maiores informações: [Lastlink Webhook Events](https://support.lastlink.com/pt-BR/articles/7238888-como-configurar-o-webhook-na-lastlink)")
