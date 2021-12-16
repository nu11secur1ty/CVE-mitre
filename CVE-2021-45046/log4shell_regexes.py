import re
from urllib.parse import unquote


FLAGS = re.IGNORECASE | re.DOTALL
ESC_DOLLAR = r'(?:\$|\\u0024||\\x24|\\0?44|%24)'
ESC_LCURLY = r'(?:\{|\\u007B|\\x7B|\\173|%7B)'
ESC_RCURLY = r'(?:\}|\\u007D|\\x7D|\\175|%7D)'
_BACKSLASH_ESCAPE_RE = re.compile(r'\\(?:u[0-9af]{4}|x[0-9af]{2}|[0-7]{,3})')
_PERCENT_ESCAPE_RE = re.compile(r'%[0-9af]{2}')


# Simple exploitation
SIMPLE_RE = re.compile(
	r'\$\{\s*jndi\s*:.*\}',
	flags=FLAGS,
)

# Simple exploitation involving an escaped value (e.g., \u006a, \156, \x64, %69)
SIMPLE_ESC_VALUE_RE = re.compile(
	r'\$\{.*(?:\\|%).*\}',
	flags=FLAGS,
)

# Nested templating
NESTED_RE = re.compile(
	r'\$\{.*\$\{.*\}.*\}',
	flags=FLAGS,
)

# Nested templating, including escaped characters
NESTED_INCL_ESCS_RE = re.compile(
	r'(?:' + ESC_DOLLAR + ESC_LCURLY + r'.*){2}' + ESC_RCURLY + r'.*' + ESC_RCURLY,
	flags=FLAGS,
)

# Any ${} tokens
ANY_RE = re.compile(
	r'\$\{.*\}',
	flags=FLAGS,
)

# Any ${} tokens, including escaped characters
ANY_INCL_ESCS_RE = re.compile(
	ESC_DOLLAR + ESC_LCURLY + r'.*' + ESC_RCURLY,
	flags=FLAGS,
)

# Any of the above, but with an unterminated token (`${jndi:addr`)
for k, r in [(k, r) for k, r in locals().items() if k.endswith('_RE')]:
	locals()[k.replace('_RE', '_OPT_RCURLY_RE')] = re.compile(
	r.pattern+ r'?',
	flags=FLAGS
)


regexes = {k: h for k, h in locals().items() if k[0] != '_' and k.endswith('_RE')}


def test(string):
	'''Scan string with all regexes.'''
	
	matches = {}
	for name, regex in regexes.items():
		if match := regex.search(string):
			matches[name] = match
	
	return matches


def test_thorough(string):
	'''Scan string with all regexes, recursively decoding escape codes.'''
	
	last_string, matches = None, {}
	
	while (
		last_string != string
		and (
			last_string is None
			or len(last_string) > len(string)
		)
	):
		if match := test(string): matches[string] = match
		
		last_string = string
		
		if _BACKSLASH_ESCAPE_RE.search(string):
			string = string.encode().decode('unicode_escape')
		
		if _PERCENT_ESCAPE_RE.search(string):
			string = unquote(string)
	
	return matches


__all__ = list(regexes.keys()) + ['test', 'test_thorough']
