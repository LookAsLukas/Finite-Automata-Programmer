from automata.fa.nfa import NFA

def regex_to_nfa(regex: str) -> NFA:
    """
    Простая обертка над встроенной функцией automata-lib для преобразования
    регулярного выражения в NFA. Библиотека сама выведет алфавит из regex.
    """
    try:
        return NFA.from_regex(regex)
    except Exception as e:
        raise ValueError(f"Неверное регулярное выражение: {str(e)}")

def validate_regex_syntax(regex: str) -> tuple[bool, str]:
    """
    Простая валидация: пытаемся скомпилировать regex через библиотеку.
    Если успех, возвращаем True, иначе False с сообщением об ошибке.
    """
    try:
        NFA.from_regex(regex)
        return True, ""
    except Exception as e:
        return False, str(e)