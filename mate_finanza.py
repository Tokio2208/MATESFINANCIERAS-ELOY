"""
Autor: Eloy
Objetivo:
Obtener el interés simple con tasa de CETES a 28 días haciendo requests en
tiempo real a las series oportunas de Banxico, enviando por email el reporte
de resultados.
Versión extendida: SMS o WhatsApp solo si no conecta el email.
"""

import os
import requests
import time as t
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
"""
Funcion 1 conexion a banxico 1
funcion 2 conexion a banxico series oportuno cetes
funcion 3 calculo de interes simple
funcion 4 conexion y envio de email
funcion 5 menú de opciones solo si lo necesitas
"""
# url es puerta, token es llave de preferencia dato oportuno
TOKEN = os.getenv('BANXICO_TOKEN')


def serie_aleatoria() -> float:
    """
    @serie_aleatoria: consulta una serie fija de Banxico y devuelve su dato
    """
    cetes_distinto = 0
    try:
        headers = {'Bmx-Token': TOKEN}
        serie = 'SF43936'
        enlace = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno'
        response = requests.get(url=enlace, headers=headers, timeout=10)
        if response.status_code == 200:
            json_response = response.json()
            cetes_distinto = float(json_response['bmx']['series'][0]['datos'][0]['dato'])
            print(f"cetes es de: {cetes_distinto}")
        elif response.status_code == 404:
            print("[Error] La serie no existe en Banxico, revise la clave.")
        else:
            print(f"[Error] Banxico respondió con código {response.status_code}, revise su token.")
    except requests.exceptions.RequestException as error:
        print(f"[Error] No se pudo conectar con Banxico: {error}")
    except (KeyError, IndexError, ValueError, TypeError) as error:
        print(f"[Error] La respuesta de Banxico no tiene el formato esperado o el dato no es numérico: {error}")
    return cetes_distinto


def cetes_28_dias() -> float:
    """
    @Cetes: la función consulta el valor de los cetes y devuelve la tasa porcentual en valor entero o decimal.
    """
    headers = {'Bmx-Token': TOKEN}
    serie = 'SF43936'
    tasa_porcentual = 0
    enlace = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno'
    try:
        response = requests.get(url=enlace, headers=headers, timeout=10)
        if response.status_code == 200:
            json_response = response.json()
            tasa_porcentual = float(json_response['bmx']['series'][0]['datos'][0]['dato'])
            print(f"El valor de cetes hoy es de : {tasa_porcentual}")
        elif response.status_code == 404:
            print("[Error] La serie no existe en Banxico, revise la clave.")
        else:
            print(f"[Error] Banxico respondió con código {response.status_code}, revise su token.")
    except requests.exceptions.RequestException as error:
        print(f"[Error] No se pudo conectar con Banxico: {error}")
    except (KeyError, IndexError, ValueError, TypeError) as error:
        print(f"[Error] La respuesta de Banxico no tiene el formato esperado o el dato no es numérico: {error}")
    return tasa_porcentual


CONTRASEÑA = os.getenv('CORREO_PASSWORD')
emisor = os.getenv('CORREO_REMITENTE')


def Calcular_interés(capital: float, dias: int, cetes: float) -> tuple:
    """
    @Calcular_interés: Calcula el interés simple usando los cetes, capital y dias.
    Regresa (tasa_interés, valor_acumulado)
    @capital: Valor entero o decimal
    @dias: Valor entero
    @cetes: Tasa de cetes obtenida con cetes_28_dias()
    """
    tasa_interés = 0.0
    valor_acumulado = 0.0
    try:
        if capital <= 0 or dias <= 0 or cetes <= 0:
            print("[Error] Capital, días y tasa de cetes deben ser mayores que 0.")
            return 0.0, 0.0
        tasa_interés = (cetes / 100) / (1 - (cetes / 100) * (28 / 360))
        valor_acumulado = capital * (1 + (tasa_interés * (dias / 360)))
    except (TypeError, ValueError, ZeroDivisionError) as error:
        print(f"[Error] No se pudo calcular el interés: {error}")
        return 0.0, 0.0
    return tasa_interés, valor_acumulado


def enviar_reporte(destinatario: str, asunto: str, reporte) -> None:
    """
    @enviar_reporte: Envía el reporte al correo electrónico. No regresa nada
    @destinatario: Dirección de correo capturada como str
    @asunto: Asunto del correo
    @reporte: Texto del reporte con la estructura de resultados
    """
    try:
        msg = MIMEText(reporte, 'plain', 'utf-8')
        msg['From'] = emisor
        msg['To'] = destinatario
        msg['Subject'] = asunto
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.ehlo()
            smtp_server.login(emisor, CONTRASEÑA)
            smtp_server.sendmail(emisor, destinatario, msg.as_string())
        print("Mensaje enviado")
    except smtplib.SMTPAuthenticationError:
        print("[Error] Gmail rechazó el usuario o la contraseña de aplicación.")
    except (smtplib.SMTPException, OSError) as error:
        print(f"[Error] No se pudo enviar el correo: {error}")


def menu():
    """
    Muestra las opciones del programa, pide la opción al usuario y llama
    a la función correspondiente hasta que decide cerrar el programa.
    return: no regresa nada, solo controla el ciclo del menú
    """
    Continuar_Programa = True

    while Continuar_Programa:
        print("\nBienvenido a FMA V1")
        print("Seleccione la operación a realizar")
        print("consultar cetes  : 1")
        print("calcular interés  : 2")
        print("salir: 3")
        try:
            Opción_Usuario = int(input("Selecciona tu opción: "))
        except ValueError:
            print("\n[Error] Ingresa un número de opción válido entre 1 y 3.")
            continue

        try:
            if Opción_Usuario == 1:
                serie_aleatoria()
            elif Opción_Usuario == 2:
                capital = float(input("ingrese su capital: "))
                dias = int(input("ingrese los dias que desea mantener su dinero: "))
                if capital <= 0 or dias <= 0:
                    print("\n[Error] El capital y dias deben de ser mayores que 0, intente de nuevo.")
                    continue
                destinatario = str(input("Ingrese el destinatario(ej. tucorreo@gmail.com): ")).strip().lower()
                if "@" not in destinatario:
                    print("\n[Error] ingrese correo válido con @")
                    continue
                asunto = str(input("Ingrese el asunto: "))
                cetes = cetes_28_dias()
                if cetes == 0:
                    print("No se obtuvo ningún valor para cetes")
                    continue
                tasa_interés, valor_acumulado = Calcular_interés(capital, dias, cetes)
                if valor_acumulado == 0:
                    print("No se generó el reporte porque el cálculo falló.")
                    continue
                interes_ganado = valor_acumulado - capital
                reporte = (
                    f"Los cetes a 28 dias: {cetes:.4f}%\n"
                    f"Tasa de rendimiento: {tasa_interés * 100:.4f}%\n"
                    f"Capital inicial: ${capital:,.2f}\n"
                    f"Días: {dias}\n"
                    f"Interés ganado: ${interes_ganado:,.2f}\n"
                    f"Valor acumulado: ${valor_acumulado:,.2f}"
                )
                print("\n" + reporte)
                t.sleep(2.0)
                enviar_reporte(destinatario, asunto, reporte)

            elif Opción_Usuario == 3:
                print("Gracias por su tiempo, saliendo del programa")
                t.sleep(5.0)
                break
            else:
                print("\n[Error] Opción no válida, elige entre 1 y 3.")
                continue
        except ValueError:
            print("\n[Error] El capital debe ser número y los días un entero. Intenta otra vez.")
            continue

        respuesta = input("\nPara continuar presiona S o Para cerrar presiona N: ").strip().lower()
        if respuesta == 'n':
            print('Gracias por tu tiempo, byeeeeee')
            print("Saliendo del programa...")
            t.sleep(5.0)
            Continuar_Programa = False

    print("Ya saliste del ciclo")


if __name__ == "__main__":
    menu()
