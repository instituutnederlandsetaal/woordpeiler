ALPHANUMERIC="a-z0-9"
DIACRITICS="àáâäåčçèéêëíîïñòóôøöúûùü"
OTHER="µβнельзя"
PUNCT="\[\]\'\.+%/°º?@|₂²;\\\\&\(\)=#,‘’-"
SOFTHYPHEN="­"

REGEX="[^$ALPHANUMERIC $DIACRITICS $OTHER $SOFTHYPHEN $PUNCT]"

echo "Executing the following regex:"
echo "$REGEX"

TOTAL=`grep -P "$REGEX" molex.txt`

echo "Linecount:"
echo "$TOTAL" | wc -l

echo "Sample:"
echo "$TOTAL" | sort