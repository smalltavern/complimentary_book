class BookViewModel:
    def __init__(self, book):
        self.title = book['title']
        self.publisher = str(book['publisher'])
        self.pubdate = book['pubdate']
        self.binding = book['binding']
        self.pages = book['pages'] or ''
        self.image = book['image']
        self.price = book['price']
        self.isbn = book['isbn']
        self.summary = book['summary'] or ''
        self.author = '、'.join(book['author'])

    @property
    def intro(self):
        intros = filter(lambda x: True if x else False, [self.author, self.publisher, self.price])

        return '/'.join(intros)


class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = None

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushu_book.books]