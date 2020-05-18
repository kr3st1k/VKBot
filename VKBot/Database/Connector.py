import asyncio
from collections import Sized
from enum import IntEnum
from collections.abc import Iterable
import warnings
import logging

import aiomysql
import mysql.connector


class DbConnVersion(IntEnum):
    SYNC = 1
    ASYNC = 2
    COUPLE = 12


# TODO rewrite docstrings


class DbConnection:
    def __init__(self, host: str, database: str, username: str, password: str, port: int,
                 driver_ver: DbConnVersion = DbConnVersion.COUPLE):
        """
        Constructor that builds Sync and/or Async versions

        Args:
            port: int port of mysql instance
            host: name of host address  example : localhost
            database: name of the database that be connected
            username: name of Database user (root)
            password: ok that's real password
            driver_ver: defines the logic of the behavior of the driver:
                DbConnVersion.COUPLE = 12 as default and says that Connector should you 2 connections: sync and async
                DbConnVersion.ASYNC = only async, THROW ERROR IF YOU WILL USE "Sync" version methods
                DbConnVersion.SYNC = only sync,  THROW ERROR IF YOU WILL USE "Async" version methods

        Raises:
            Exception if driver cannot connect to the DB
        Warnings:
            RuntimeWarning if inside the class some method tried to connect while connection was opened

        """
        # sync version of driver
        self._port = port
        self.driver_ver = driver_ver
        self._password = password
        self._username = username
        self._database = database
        self._host = host

    def _base_execute_and_iter(self, executed: str) -> Iterable:
        """
        Execute str and returns Iterable object

        Args:
            executed: str type that will be executed in DataBase

        Returns:
            Iterable: if select was success
            NoneType: if select was failed
        Raises:
            Exception that was taken by critical runtime error
        """
        _connection = mysql.connector.connect(host=self._host,
                                              database=self._database,
                                              user=self._username,
                                              password=self._password)

        records = None
        cursor = None
        try:
            cursor = _connection.cursor()
            cursor.execute(executed)
            records = cursor.fetchall()
            # TODO rewrite Exception
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            if _connection.is_connected():
                _connection.close()
                cursor.close()
        return records

    def _base_execute(self, executed: str):
        """
        Only execute str as void function

        Args:
            executed: str type that will be executed in DataBase

        Returns:
            NoneType: Void
        Raises:
            Exception that was taken by critical runtime error
        """
        _connection = mysql.connector.connect(host=self._host,
                                              database=self._database,
                                              user=self._username,
                                              password=self._password)

        records = None
        cursor = None
        try:
            cursor = _connection.cursor()
            cursor.execute(executed)
            emp_no = cursor.lastrowid
            # TODO rewrite Exception
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            _connection.commit()
            if _connection.is_connected():
                _connection.close()
                cursor.close()

    def _select_all_table(self, table_name: str) -> Iterable:
        """
        Gives selected table (all columns)

        Args:
            table_name: string of Table that required

        Returns:
            Iterable: returns iterable top of objects with
            NoneType: if select was failed
        """
        return self._base_execute_and_iter("SELECT * FROM {0}".format(table_name))

    def _select_top(self, table_name: str, top: int) -> Iterable:
        """
        Gives selected top with all columns

        Args:
            table_name: string of Table that required
            top: number of needed rows

        Returns:
            Iterable: returns iterable top of objects with all columns
            NoneType: if select was failed
        """
        return self._base_execute_and_iter("SELECT * FROM {0} LIMIT {1}".format(table_name, str(top)))

    def select_all_table(self, table_name: str, column_names: [str] = None) -> Iterable:
        """
        Overload of select_all_table that's apply names of _selected columns
        Gives selected table (all columns or taken args columns)

        Args:
            column_names: list of strings that contains names of table's columns (can be null)
            table_name: string of Table that required

        Returns:
            Iterable and Sized: returns iterable top of objects with
            NoneType: if select was failed
        """
        if column_names is None:
            return self._select_all_table(table_name)
        else:
            return self._base_execute_and_iter("SELECT {0} FROM {1}"
                                               .format(', '.join(name for name in column_names), table_name))

    def select_top(self, table_name: str, top: int, column_names: [str] = None) -> Iterable:
        """
        Gives selected top with all columns or taken columns

        Args:
            column_names: list of strings that contains names of table's columns
            table_name: string of Table that required
            top: number of needed rows

        Returns:
            Iterable: returns iterable top of objects with all columns
            NoneType: if select was failed
        """
        if column_names is None:
            return self._select_top(table_name, top)
        else:
            return self._base_execute_and_iter("SELECT {0} FROM {1} LIMIT {2}"
                                               .format(', '.join(name for name in column_names), table_name, str(top)))

    def select_where(self, table_name: str, where_condition: dict) -> Iterable:
        """
        Method that select ony conditional rows(row)

        Examples:
            .select_where('my_table', {'id':20000, 'name':'karton'})

            .select_where('my_table', {'id':20000})
        Args:
            where_condition(dict key: string, value: object): key value pairs of find operation
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        print("SELECT * FROM {0} WHERE {1}"
                                           .format(table_name, ' AND '.join("{0}={1}"
                                                                            .format(item,
                                                                                    where_condition[item]
                                                                                    if type(
                                                                                        where_condition[item]) != str
                                                                                    else "'" + where_condition[
                                                                                        item] + "'")
                                                                            for item in where_condition)))
        return self._base_execute_and_iter("SELECT * FROM {0} WHERE {1}"
                                           .format(table_name, ' AND '.join("{0}={1}"
                                                                            .format(item,
                                                                                    where_condition[item]
                                                                                    if type(
                                                                                        where_condition[item]) != str
                                                                                    else "'" + where_condition[
                                                                                        item] + "'")
                                                                            for item in where_condition)))

    async def _connect_to_async(self, loop):
        _async_conn = None
        try:
            _async_conn = await aiomysql.create_pool(host=self._host, port=3306,
                                                     user=self._username, password=self._password,
                                                     db=self._database, loop=loop)
            return _async_conn
        except Exception as e:
            logging.critical(e)
            raise e

    async def _base_execute_async(self, execute: str, loop) -> Iterable:
        """
            Asynchronous version of protected method _base_select

        Args:
            loop (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            execute: str type that will be executed in DataBase

        Returns:
            Iterable: if select was success
            NoneType: if select was failed
        Raises:
            Exception that
        """
        _aw_pool_result = None
        _as_pool = await self._connect_to_async(loop)
        async with _as_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(execute)
                _aw_pool_result = await cur.fetchall()
        _as_pool.close()
        await _as_pool.wait_closed()
        return _aw_pool_result

    async def select_all_table_async(self, table_name: str, loop) -> Iterable:
        """
        asynchronous version of protected method select_all_table
        Gives selected table (all columns)

        Args:
            table_name: string of Table that required
            loop (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
        Returns:
            Iterable: returns iterable top of objects with
            NoneType: if select was failed
        """
        return await self._base_execute_async("SELECT * FROM {0}".format(table_name), loop)

    async def select_top_async(self, table_name: str, top: int, loop) -> Iterable:
        """
        Asynchronous version of protected method select_top
        Gives selected top with all columns

        Args:
            loop: (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            table_name: string of Table that required
            top: number of needed rows

        Returns:
            Iterable: returns iterable top of objects with all columns
            NoneType: if select was failed
        """
        return await self._base_execute_async("SELECT * FROM {0} LIMIT {1}".format(table_name, str(top)), loop)

    async def select_all_table_async(self, column_names: [str], table_name: str, loop) -> Iterable:
        """
        Overload of select_all_table that's apply names of selected columns
        Gives selected table (all columns)

        Args:
            loop: (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            column_names: list of strings that contains names of table's columns
            table_name: string of Table that required

        Returns:
            Iterable: returns iterable top of objects with
            NoneType: if select was failed
        """
        return await self._base_execute_async("SELECT {0} FROM {1}"
                                              .format(', '.join(name for name in column_names), table_name), loop)

    async def select_top_async(self, column_names: [str], table_name: str, top: int, loop) -> Iterable:
        """
        Gives selected top with all columns

        Args:
            loop: (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            column_names: list of strings that contains names of table's columns
            table_name: string of Table that required
            top: number of needed rows

        Returns:
            Iterable: returns iterable top of objects with all columns
            NoneType: if select was failed
        """
        return await self._base_execute_async("SELECT {0} FROM {1} LIMIT {2}"
                                              .format(', '.join(name for name in column_names), table_name, str(top)),
                                              loop)

    def insert_into(self, table_name: str, dict_of_inserts: dict) -> bool:
        """
        Method that insert key:value pairs into table

        Examples:
            .insert_into('my_table', {'id':20000, 'name':'karton', 'surname': 'bot'})
        Args:
            dict_of_inserts(dict key: string, value: object): key value pairs of insertion operation
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """

        try:
            self._base_execute("INSERT INTO {0} ({1}) VALUES ({2})"
                               .format(table_name,
                                       ', '.join(column_name for column_name in dict_of_inserts.keys()),
                                       ', '.join(str(column_value) if type(column_value) != str
                                                 else "'" + str(column_value) + "'"
                                                 for column_value in dict_of_inserts.values())))
            return True
        except Exception as e:
            logging.warn("Insert failed and exception was taken {}".format(e))
            return False

    def delete_where(self, table_name: str, where_condition: dict) -> bool:
        """
        Delete method in condition that identity row that should be deleted

        Examples:
            .delete_where('my_table', {'id': 123})
            .delete_where('my_table', {'nickname': 'karton'})
        Args:
            where_condition (dict key: string, value: object): condition that identity row that should be deleted
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        try:
            # TODO rewrite
            if len(where_condition) == 1:
                where_str = ""
                for i, item in enumerate(where_condition):
                    # TODO add here any case where + len > 1
                    where_str += "{0}={1}".format(item, where_condition[item]
                    if type(where_condition[item]) != str
                    else "'" + where_condition[item] + "'")
                    print("DELETE FROM {0} WHERE {1}".format(table_name, where_str))
                self._base_execute("DELETE FROM {0} WHERE {1}".format(table_name, where_str))
                return True
            else:
                raise NotImplementedError("Uses only one condition in where statement")
        except Exception as e:
            logging.warning("Delete failed and exception was taken {0}".format(e))
            return False

    def update_where(self, table_name: str, where_condition: dict, dict_of_updates: dict) -> bool:
        """
        Method that changes some key:value pairs in row that finds by where_condition

        Examples:
            .insert_into('my_table', {'id':20000, 'name':'karton', 'surname': 'bot'})
        Args:
            where_condition (dict key: string, value: object): condition that identity row that should be deleted
            dict_of_updates(dict key: string, value: object): key value pairs of insertion operation
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        try:
            var = "UPDATE {0} SET {1} WHERE {2}".format(table_name,
                                                        ', '.join("{0}={1}".format(item,
                                                                                   dict_of_updates[item]
                                                                                   if type(dict_of_updates[item]) != str
                                                                                   else "'" + dict_of_updates[
                                                                                       item] + "'")
                                                                  for item in dict_of_updates),
                                                        ' AND '.join("{0}={1}"
                                                                     .format(item,
                                                                             where_condition[item]
                                                                             if type(where_condition[item]) != str
                                                                             else "'" + where_condition[item] + "'")
                                                                     for item in where_condition))
            self._base_execute(var)
            return True
        except Exception as e:
            logging.warning("Update failed and exception was taken {}".format(e))
            return False

    async def insert_into_async(self, table_name: str, dict_of_inserts: dict, loop) -> bool:
        """
        Async version of insert_into
        Method that insert key:value pairs into table

        Examples:
            await .insert_into('my_table', {'id':20000, 'name':'karton', 'surname': 'bot'}, loop)
        Args:
            loop (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            dict_of_inserts(dict key: string, value: object): key value pairs of insertion operation
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        try:
            await self._base_execute_async("INSERT INTO {0} ({1}) VALUES ({2})"
                                           .format(table_name,
                                                   ', '.join(column_name for column_name in dict_of_inserts.keys()),
                                                   ', '.join(col_value for col_value in dict_of_inserts.values())),
                                           loop)
            return True
        except Exception as e:
            logging.warning("Insert failed and exception was taken {}".format(e))
            return False

    async def delete_where_async(self, table_name: str, where_condition: dict, loop) -> bool:
        """
        Async version of delete_where
        Delete method in condition that identity row that should be deleted

        Examples:
            await .delete_where('my_table', {'id': 123}, async_loop)

        Args:
            loop (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            where_condition (dict key: string, value: object): condition that identity row that should be deleted
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        try:
            if len(where_condition) == 1:
                where_str = ""
                for i, item in enumerate(where_condition):
                    # TODO add here any case where + len > 1
                    where_condition += "{0}={1}".format(item.key(), item.value())
                await self._base_execute_async("DELETE FROM {0} WHERE {1}".format(table_name, where_condition), loop)
                return True
            else:
                raise NotImplementedError("Uses only one condition in where statement")
        except Exception as e:
            logging.warn("Delete failed and exception was taken {0}".format(e))
            return False

    async def update_where_async(self, table_name: str, where_condition: dict, dict_of_updates: dict, loop) -> bool:
        """
        Method that changes some key:value pairs in row that finds by where_condition

        Examples:
            .insert_into('my_table', {'id':20000, 'name':'karton', 'surname': 'bot'})
        Args:
            loop (asyncio Async POOL): pool of asyncio io that can be got by call asyncio.get_pool
            where_condition : (dict  key: string, value: object) condition that identity row that should be deleted
            dict_of_updates: (dict key: string, value: object) key value pairs of insertion operation
            table_name (str): name of current table that w

        Returns:
            bool: True if insert operation was success and False if take any Exception
        """
        try:
            if len(where_condition) == 1:
                # TODO add here any case where + len > 1
                where = str()
                for item in where_condition:
                    where_condition += "{0}={1}".format(item.key(), item.value())

                updates_str = ""

                for i, seq in enumerate(dict_of_updates):
                    updates_str += "{0}={1}".format(seq.key(), str(seq.value()))
                    if i != len(dict_of_updates) - 1:
                        updates_str += ", "

                await self._base_execute_async("UPDATE {0} SET {1} WHERE {2}"
                                               .format(table_name, updates_str, where), loop)
                return True
            else:

                raise NotImplementedError("Uses only one condition in where statement")
        except Exception as e:
            logging.warn("Update failed and exception was taken {}".format(e))
            return False
