#!/bin/bash
# Script de diagnostic pour tester la connexion SiYuan

echo "🔍 Diagnostic de connexion SiYuan"
echo "=================================="
echo ""

# Demander l'URL
read -p "URL SiYuan [http://192.168.1.11:6806]: " SIYUAN_URL
SIYUAN_URL=${SIYUAN_URL:-http://192.168.1.11:6806}

# Demander le token
read -sp "Token SiYuan: " SIYUAN_TOKEN
echo ""
echo ""

# Test 1: Ping basique
echo "Test 1: Ping de l'URL..."
if curl -s -o /dev/null -w "%{http_code}" "$SIYUAN_URL" > /dev/null 2>&1; then
    echo "✅ SiYuan répond sur $SIYUAN_URL"
else
    echo "❌ Impossible de contacter $SIYUAN_URL"
    echo "   Vérifiez que SiYuan est lancé et l'URL est correcte"
    exit 1
fi

# Test 2: API sans auth
echo ""
echo "Test 2: Appel API /api/system/version..."
VERSION_RESPONSE=$(curl -s "$SIYUAN_URL/api/system/version")
echo "Response: $VERSION_RESPONSE"

# Test 3: API avec token (format 1)
echo ""
echo "Test 3: Test avec 'Authorization: Token XXX'..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST "$SIYUAN_URL/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

echo "HTTP Code: $HTTP_CODE"
echo "Response: $BODY"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Connexion réussie avec ce format !"
else
    echo "❌ Échec avec ce format"
fi

# Test 4: API avec token (format 2 - sans "Token")
echo ""
echo "Test 4: Test avec 'Authorization: XXX' (sans Token)..."
RESPONSE2=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST "$SIYUAN_URL/api/notebook/lsNotebooks" \
  -H "Authorization: $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')

HTTP_CODE2=$(echo "$RESPONSE2" | grep "HTTP_CODE:" | cut -d: -f2)
BODY2=$(echo "$RESPONSE2" | grep -v "HTTP_CODE:")

echo "HTTP Code: $HTTP_CODE2"
echo "Response: $BODY2"

if [ "$HTTP_CODE2" = "200" ]; then
    echo "✅ Connexion réussie avec ce format !"
else
    echo "❌ Échec avec ce format"
fi

# Test 5: Headers détaillés
echo ""
echo "Test 5: Diagnostic complet avec headers..."
curl -v -X POST "$SIYUAN_URL/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' 2>&1 | grep -E "^[<>]|HTTP"

echo ""
echo "=================================="
echo "💡 Résumé:"
echo "   URL testée: $SIYUAN_URL"
echo "   Token (premiers caractères): ${SIYUAN_TOKEN:0:20}..."
echo ""
echo "Si tous les tests échouent:"
echo "1. Vérifiez que SiYuan est en 'Mode serveur' (Paramètres → À propos)"
echo "2. Vérifiez que l'API est activée"
echo "3. Essayez avec http://localhost:6806 au lieu de l'IP"
echo "4. Regénérez le token dans SiYuan"
echo ""
