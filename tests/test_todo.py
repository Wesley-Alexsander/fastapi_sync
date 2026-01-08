from http import HTTPStatus

from fastapi_sincrono.models import TodoStatus
from tests.conftest import TodoFactory


def test_create_todo(client, token):
    responde = client.post(
        '/todo/',
        headers={'authorization': f'bearer {token}'},
        json={
            'title': 'test todo',
            'description': 'this is a test todo item.',
            'state': 'pending',
        },
    )

    assert responde.status_code == HTTPStatus.OK
    assert responde.json() == {
        'id': 1,
        'title': 'test todo',
        'description': 'this is a test todo item.',
        'state': 'pending',
    }


def test_list_todos_should_return_5_todos(client, token, user, session):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todo/',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(
    client, token, user, session
):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todo/?offset=1&limit=2',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title_should_return_filtered_todos(
    client, token, user, session
):
    expected_todos = 5
    session.bulk_save_objects([
        *TodoFactory.build_batch(5, user_id=user.id, title='Buy groceries'),
        *TodoFactory.build_batch(3, user_id=user.id, title='Give gifts'),
    ])
    session.commit()

    response = client.get(
        '/todo/?title=Buy',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_description_should_return_filtered_todos(
    client, token, user, session
):
    expected_todos = 3
    session.bulk_save_objects([
        *TodoFactory.build_batch(
            3, user_id=user.id, description='Last minute Buy'
        ),
        *TodoFactory.build_batch(
            2, user_id=user.id, description='Remeber give gifts'
        ),
    ])
    session.commit()

    response = client.get(
        '/todo/?description=Last',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_state_should_return_filtered_todos(
    client, token, user, session
):
    expected_todos = 1
    session.bulk_save_objects([
        *TodoFactory.build_batch(3, user_id=user.id, state=TodoStatus.pending),
        *TodoFactory.build_batch(2, user_id=user.id, state=TodoStatus.trash),
        *TodoFactory.build_batch(1, user_id=user.id, state=TodoStatus.doing),
    ])
    session.commit()

    response = client.get(
        '/todo/?state=doing',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_delete_todo_should_return_success_message(
    client, token, user, session
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todo/{todo.id}',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Todo deleted successfully'}


def test_delete_todo_should_return_not_found_message(client, token):
    response = client.delete(
        f'/todo/{9999}',
        headers={'authorization': f'bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_patch_todo_should_update_and_return_todo(
    client, token, user, session
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todo/{todo.id}',
        headers={'authorization': f'bearer {token}'},
        json={
            'title': 'Updated title',
            'description': 'Updated description',
            'state': 'doing',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': todo.id,
        'title': 'Updated title',
        'description': 'Updated description',
        'state': 'doing',
    }


def test_patch_todo_should_return_not_found_message(client, token):
    response = client.patch(
        f'/todo/{9999}',
        headers={'authorization': f'bearer {token}'},
        json={
            'title': 'Updated title',
            'description': 'Updated description',
            'state': 'doing',
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
