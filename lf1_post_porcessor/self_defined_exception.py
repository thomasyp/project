
class CustomError(Exception):
    def __init__(self, errorinfo):
        super().__init__(self)
        self.errorinfo = errorinfo
    def __str__(self):
        return self.errorinfo



if __name__ == '__main__':
    try:
        raise CustomError('test')
    except CustomError as e:
        print(e)