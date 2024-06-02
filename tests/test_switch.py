import pytest

from tests.helpers.bot_fixtures import bot_fixture


UWUIFY = 'uwuify'
USERINFO = 'userinfo'

@pytest.fixture(autouse=True, scope='module')
def bot_fixture_():
    with bot_fixture() as result:
        yield result

@pytest.mark.asyncio
async def test_message_when_inactive(conv):
    await conv.send_message("hello")
    response = await conv.get_response()
    assert 'None of the bots are active' in response.message


@pytest.mark.asyncio
async def test_switch_with_message(conv):
    await conv.send_message("/switch")
    response = await conv.get_response()
    assert 'No bot specified' in response.message

    await conv.send_message(UWUIFY)
    response = await conv.get_response()
    assert f"Activated {UWUIFY}" in response.message

    await conv.send_message("hello")
    response = await conv.get_response()
    assert response.message == 'hewwwOwO'


@pytest.mark.asyncio
async def test_switch_directly(conv):
    await conv.send_message(f"/switch {UWUIFY}")
    response = await conv.get_response()
    assert f"Activated {UWUIFY}" in response.message

    await conv.send_message("hello")
    response = await conv.get_response()
    assert response.message == 'hewwwOwO'


@pytest.mark.asyncio
async def test_switch_independence(conv, group):
    await conv.send_message(f"/switch {UWUIFY}")
    response = await conv.get_response()
    assert f"Activated {UWUIFY}" in response.message

    await group.send_message(f"/switch {USERINFO}")
    response = await group.get_response()
    assert f"Activated {USERINFO}" in response.message

    await conv.send_message("hello")
    response = await conv.get_response()
    assert response.message == 'hewwwOwO'

    await group.send_message("hello")
    response = await group.get_response()
    assert f"from_user.id" in response.message

