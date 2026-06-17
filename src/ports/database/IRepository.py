from typing import Generic, Protocol, TypeVar

TDomain = TypeVar("TDomain", bound=object)
TId = TypeVar("TId", bound=object, contravariant=True)
TListField = TypeVar("TListField", bound=str)


class IRepository(Generic[TDomain, TId, TListField], Protocol):
    """
    Interface for a generic repository that defines basic CRUD operations.
    """

    async def list(
        self, filters: dict[TListField, int | str | bool] = {}
    ) -> list[TDomain]:
        """
        Get an entity by its ID.

        :param filters: A dictionary of filter criteria to apply when listing entities. if no filters are provided, all entities will be returned.
        :return: A list of entities matching the filter criteria.
        """
        ...

    async def get(self, id: TId) -> TDomain | None:
        """
        Get an entity by its ID.

        :param id: The ID of the entity to be retrieved.
        :return: The entity with the specified ID.
        """
        ...

    async def upsert_many(self, entities: list[TDomain]) -> list[TDomain]:
        """
        Insert a list of entities or update existing ones in the repository.

        :param entities: The list of entities to be inserted or updated.

        :return: The list of entities that were upserted.
        """
        ...

    async def upsert(self, entity: TDomain) -> TDomain | None:
        """
        Insert a new entity or update an existing one in the repository.

        :param entity: The entity to be inserted or updated.

        :return: The entity that was inserted or updated.
        """
        ...

    async def add_many(self, entities: list[TDomain]) -> list[TDomain]:
        """
        Insert a list of new entities into the repository.

        :param entities: The list of entities to be inserted.

        :return: The list of entities that were added.
        """
        ...

    async def add(self, entity: TDomain) -> TDomain | None:
        """
        Insert a new entity into the repository.

        :param entity: The entity to be inserted.

        :return: The entity that was added.
        """
        ...

    async def update_many(self, entities: list[TDomain]) -> list[TDomain]:
        """
        Update a list of existing entities in the repository.

        :param entities: The list of entities to be updated.

        :return: The list of entities that were updated.
        """
        ...

    async def update(self, entity: TDomain) -> TDomain | None:
        """
        Update an existing entity in the repository.

        :param entity: The entity to be updated.

        :return: The entity that was updated.
        """
        ...


# pas utilisé :    async def delete_many(self, ids: list[TId]) -> list[bool]:
# pas utilisé :        """
# pas utilisé :        Delete multiple entities from the repository by their IDs.
# pas utilisé :
# pas utilisé :        :param ids: The IDs of the entities to be deleted.
# pas utilisé :
# pas utilisé :        :return: A list of booleans indicating the success of each deletion.
# pas utilisé :        """
# pas utilisé :        ...
# pas utilisé :
# pas utilisé :    async def delete(self, id: TId) -> bool:
# pas utilisé :        """
# pas utilisé :        Delete an entity from the repository by its ID.
# pas utilisé :
# pas utilisé :        :param id: The ID of the entity to be deleted.
# pas utilisé :
# pas utilisé :        :return: True if the entity was deleted, False otherwise.
# pas utilisé :        """
# pas utilisé :        ...
# pas utilisé :
# pas utilisé :    async def clear(self) -> bool:
# pas utilisé :        """
# pas utilisé :        Clear entities from the repository based on filter criteria. (delete ALL entities !! like a "TRUNCATE" operation in SQL)
# pas utilisé :
# pas utilisé :        :return: True if the entities were cleared, False otherwise.
# pas utilisé :        """
# pas utilisé :        ...
