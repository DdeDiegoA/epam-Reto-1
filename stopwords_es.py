"""Lista curada de stopwords en español (artículos, pronombres, preposiciones,
conjunciones y verbos auxiliares de alta frecuencia y bajo valor semántico).

Se usa solo para el cálculo de palabras frecuentes, no para el texto limpio
que se guarda en el dataset final (ese conserva todas las palabras).
"""

STOPWORDS_ES = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con",
    "contra", "cual", "cuando", "de", "del", "desde", "donde", "durante", "e",
    "el", "ella", "ellas", "ellos", "en", "entre", "era", "erais", "eran",
    "eras", "eres", "es", "esa", "esas", "ese", "eso", "esos", "esta",
    "estaba", "estabais", "estaban", "estabas", "estad", "estada", "estadas",
    "estado", "estados", "estamos", "estando", "estar", "estaremos",
    "estará", "estarán", "estarás", "estaré", "estaréis", "estaría",
    "estarían", "estas", "este", "esto", "estos", "estoy", "estuve",
    "estuviera", "estuvieron", "fue", "fuera", "fueron", "fui", "fuimos",
    "ha", "habéis", "había", "habían", "han", "has", "hasta", "hay", "he",
    "la", "las", "le", "les", "lo", "los", "más", "me", "mi", "mis",
    "mucho", "muchos", "muy", "nada", "ni", "no", "nos", "nosotras",
    "nosotros", "o", "os", "otra", "otras", "otro", "otros", "para", "pero",
    "poco", "por", "porque", "pues", "que", "qué", "quien", "quienes", "se",
    "sea", "sean", "según", "ser", "si", "sí", "sido", "siendo", "sin",
    "sobre", "sois", "somos", "son", "soy", "su", "sus", "también", "tan",
    "tanto", "te", "tenía", "tener", "tengo", "ti", "todo", "todos", "tu",
    "tus", "un", "una", "uno", "unos", "y", "ya", "yo",
}
