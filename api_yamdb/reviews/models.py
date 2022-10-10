import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
]


class User(AbstractUser):
    password = models.CharField('password', max_length=128, blank=True)
    email = models.EmailField('email address', blank=False, unique=True)
    bio = models.TextField('Биография', blank=True, )
    role = models.CharField(
        'Роль',
        max_length=max([len(item) for item, _ in ROLE_CHOICES]),
        choices=ROLE_CHOICES,
        default=USER,
        blank=False,
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=50,
        blank=True,
    )

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER


class CategoryGenreAbstract(models.Model):
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField(
        'Слаг',
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Недопустимый символ в слаге категории.')
        ])

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryGenreAbstract):
    class Meta(CategoryGenreAbstract.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreAbstract):
    class Meta(CategoryGenreAbstract.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        validators=[
            MaxValueValidator(dt.date.today().year,
                              'Проверьте год произведения.')
        ],
        null=True,
        blank=True,
        db_index=True
    )
    description = models.TextField('Описание', )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   related_name='genres', through='GenreTitle')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)
        indexes = [
            models.Index(fields=['year']),
        ]

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведения'

    def __str__(self):
        return f'{self.title}, {self.genre}'


class ReviewAndCommentDataAbstractModel(models.Model):
    """ Искусственная какая-то абстракция(((. """

    text = models.TextField(verbose_name='Текст', )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)
        default_related_name = 'reviews'

    def __str__(self):
        return self.text[:15]


class Review(ReviewAndCommentDataAbstractModel):
    title = models.ForeignKey(
        Title,
        verbose_name='Название',
        on_delete=models.CASCADE,
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Значения от 1 до 10'),
            MaxValueValidator(10, 'Значения от 1 до 10')
        ],
        default=1,
    )

    class Meta(ReviewAndCommentDataAbstractModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]
        default_related_name = 'reviews'


class Comment(ReviewAndCommentDataAbstractModel):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
    )

    class Meta(ReviewAndCommentDataAbstractModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
