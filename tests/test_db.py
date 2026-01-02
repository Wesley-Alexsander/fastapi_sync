from sqlalchemy import select

from fastapi_sincrono.models import User


def test_create_user(session):
    user = User(username='Rex', email='TIRex@sauro.com', password='RexN2123')
    session.add(user)  # Adiciona dados a sessão singleton
    session.commit()  # persiste os dados e operações da sessão no banco
    # session.refresh(user)  # atualiza o obj python com os dados do banco

    result = session.scalar(
        select(User).where(User.email == 'TIRex@sauro.com')
    )  # registro no formato objeto scalar

    assert result.username == 'Rex'
