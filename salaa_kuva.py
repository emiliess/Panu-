from cryptography.fernet import Fernet

# Luo salausavain ja tallenna se tiedostoon
def luo_salausavain():
    avain = Fernet.generate_key()
    with open("salausavain.key", "wb") as avaintiedosto:
        avaintiedosto.write(avain)

# Salaa kuvatiedosto
def salaa_tiedosto(tiedostonimi):
    # Lue salausavain
    with open("salausavain.key", "rb") as avaintiedosto:
        avain = avaintiedosto.read()
    cipher = Fernet(avain)

    # Lue alkuperäinen tiedosto ja salaa sen sisältö
    with open(tiedostonimi, "rb") as tiedosto:
        data = tiedosto.read()
    salattu_data = cipher.encrypt(data)

    # Tallenna salattu tiedosto
    with open(tiedostonimi + ".enc", "wb") as salattu_tiedosto:
        salattu_tiedosto.write(salattu_data)
    print(f"Tiedosto '{tiedostonimi}' salattu onnistuneesti!")

if __name__ == "__main__":
    # Luo salausavain (vain kerran)
    luo_salausavain()
    
    # Salaa kuvatiedosto (anna tiedoston nimi)
    salaa_tiedosto("Kuva.png.jpg")