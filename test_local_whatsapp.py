import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.notifiers.whatsapp import WhatsAppNotifier

print("\n--- Teste de Envio do ZapDiario (Green API) ---\n")

# Pedir input do usuario
instance_id = input("1. Cole o ID da instancia (ex: 1101869811): ")
api_token = input("2. Cole o Token (ex: 8881aa...): ")
phone = input("3. Cole o telefone (ex: 558591617709): ")

# Set environment variables
os.environ['GREEN_API_INSTANCE_ID'] = instance_id.strip()
os.environ['GREEN_API_TOKEN'] = api_token.strip()
os.environ['WHATSAPP_RECIPIENT_PHONE'] = phone.strip()

print("\nTentando enviar mensagem...")
notifier = WhatsAppNotifier()
result = notifier.send_message("Teste do ZapDiario: Olá mundo! 🌍")

if result:
    print("\n✅ Sucesso! Verifique seu WhatsApp.")
    # Ask if user wants to save to .env
    save = input("\nQuer salvar essas credenciais no arquivo .env para futuros testes? (s/n): ")
    if save.lower() == 's':
        with open('.env', 'w') as f:
            f.write(f"GREEN_API_INSTANCE_ID={instance_id.strip()}\n")
            f.write(f"GREEN_API_TOKEN={api_token.strip()}\n")
            f.write(f"WHATSAPP_RECIPIENT_PHONE={phone.strip()}\n")
        print("Salvo em .env! (Não comite esse arquivo no git).")
else:
    print("\n❌ Falha no envio. Verifique os dados.")
