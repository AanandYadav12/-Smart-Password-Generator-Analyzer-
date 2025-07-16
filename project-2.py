import streamlit as st
import random, math, hashlib, requests

st.title("🔐 Smart Password Generator & Analyzer")

length = st.slider("Password Length", min_value=4, max_value=64, value=12)
include_upper = st.checkbox("Include Uppercase Letters", value=True)
include_lower = st.checkbox("Include Lowercase Letters", value=True)
include_digits = st.checkbox("Include Digits", value=True)
include_symbols = st.checkbox("Include Symbols", value=True)

char_pool = ""
mandatory_sets = []

if include_upper:
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    char_pool += upper
    mandatory_sets.append(upper)
if include_lower:
    lower = "abcdefghijklmnopqrstuvwxyz"
    char_pool += lower
    mandatory_sets.append(lower)
if include_digits:
    digits = "0123456789"
    char_pool += digits
    mandatory_sets.append(digits)
if include_symbols:
    symbols = "!@#$%^&*()-_=+[]{}"
    char_pool += symbols
    mandatory_sets.append(symbols)

def gen_password():
    while True:
        password = ''.join(random.choices(char_pool, k=length))
        if all(any(c in group for c in password) for group in mandatory_sets):
            return password

def entropy_bar(entropy):
    blocks = int(min(entropy / 2, 40))
    return "[" + "#" * blocks + "-" * (40 - blocks) + "]"

def check_breach(password):
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    try:
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        res = requests.get(url)
        hashes = (line.split(":") for line in res.text.splitlines())
        for h, count in hashes:
            if h.strip().upper() == suffix:
                return f"⚠️ Found in breaches {count} times! DO NOT USE."
        return "✅ Not found in known breaches."
    except:
        return "⚠️ Error: Couldn't check breach status."

if st.button("Generate Password"):
    if not char_pool:
        st.error("Please select at least one character type.")
    else:
        password = gen_password()
        pool_size = len(char_pool)
        total_possible = pool_size ** length
        entropy = round(length * math.log2(pool_size), 2)
        strength = ("Very Weak" if total_possible < 1_000_000 else
                    "Medium" if total_possible < 1_000_000_000 else
                    "Very Strong")
        entropy_level = ("Low Entropy" if entropy < 40 else
                         "Medium Entropy" if entropy < 60 else
                         "Good Entropy" if entropy < 80 else
                         "Excellent Entropy")
        crack_time = total_possible / 1_000_000_000
        time_text = ("<1s" if crack_time < 1 else
                     f"{int(crack_time)}s" if crack_time < 60 else
                     f"{int(crack_time/60)}min" if crack_time < 3600 else
                     f"{int(crack_time/3600)}h" if crack_time < 86400 else
                     f"{int(crack_time/86400)}d" if crack_time < 31536000 else
                     f"{int(crack_time/31536000)}y")

        st.text_input("🔑 Generated Password", value=password)
        st.markdown(f"- **Strength**: `{strength}`")
        st.markdown(f"- **Entropy**: `{entropy} bits` → `{entropy_level}`")
        st.markdown(f"- **Estimated Crack Time**: `{time_text}`")
        st.markdown(f"- **Entropy Visual**: `{entropy_bar(entropy)}`")
        st.markdown(f"- **Breach Status**: `{check_breach(password)}`")

manual = st.text_input("🔎 Check Breach for Custom Password")
if manual:
    st.markdown(f"Result: `{check_breach(manual)}`")
