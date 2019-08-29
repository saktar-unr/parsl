from abc import ABCMeta, abstractmethod, abstractproperty
from concurrent.futures import Future

from typing import Any, List, Optional


# for type checking:
from parsl.providers.provider_base import ExecutionProvider


class ParslExecutor(metaclass=ABCMeta):
    """Define the strict interface for all Executor classes.

    This is a metaclass that only enforces concrete implementations of
    functionality by the child classes.

    In addition to the listed methods, a ParslExecutor instance must always
    have a member field:

       label: str - a human readable label for the executor, unique
              with respect to other executors.

    An executor may optionally expose:

       storage_access: List[parsl.data_provider.staging.Staging] - a list of staging
              providers that will be used for file staging. In the absence of this
              attribute, or if this attribute is `None`, then a default value of
              `parsl.data_provider.staging.default_staging` will be used by the
              staging code.

              Typechecker note: Ideally storage_access would be declared on executor
              __init__ methods as List[Staging] - however, lists are by default
              invariant, not co-variant, and it looks like @typeguard cannot be
              persuaded otherwise. So if you're implementing an executor and want to
              @typeguard the constructor, you'll have to use List[Any] here.
    """

    # mypy doesn't actually check that the below are defined by
    # concrete subclasses - see  github.com/python/mypy/issues/4426
    # and maybe PEP-544 Protocols

    label: str
    provider: ExecutionProvider
    managed: bool
    status: Any  # what is this? used by strategy
    outstanding: Any  # what is this? used by strategy
    working_dir: Optional[str]
    storage_access: Optional[List[Any]]

    @abstractmethod
    def start(self) -> None:
        """Start the executor.

        Any spin-up operations (for example: starting thread pools) should be performed here.
        """
        pass

    @abstractmethod
    def submit(self, func: Any, *args: Any, **kwargs: Any) -> Future:
        """Submit.

        We haven't yet decided on what the args to this can be,
        whether it should just be func, args, kwargs or be the partially evaluated
        fn

        BENC: based on how ipp uses this, this follows the semantics of async_apply from ipyparallel.
        Based on how the thread executor works, its:

            https://docs.python.org/3/library/concurrent.futures.html
            Schedules the callable, fn, to be executed as fn(*args **kwargs) and returns a Future object representing the execution of the callable.

        These are consistent

        The value returned must be some kind of future that I'm a bit vague on the
        strict requirements for:

             it must be possible to assign a retries_left member slot to that object.
             it's referred to as exec_fu - but it's whatever the underlying executor returns (ipp, thread pools, whatever) which has some Future-like behaviour
                  - so is it always the case that we can add retries_left? (I guess the python model permits that but it's a bit type-ugly)


        """
        pass

    @abstractmethod
    def scale_out(self, blocks: int) -> None:
        """Scale out method.

        We should have the scale out method simply take resource object
        which will have the scaling methods, scale_out itself should be a coroutine, since
        scaling tasks can be slow.
        """
        pass

    @abstractmethod
    def scale_in(self, blocks: int) -> None:
        """Scale in method.

        Cause the executor to reduce the number of blocks by count.

        We should have the scale in method simply take resource object
        which will have the scaling methods, scale_in itself should be a coroutine, since
        scaling tasks can be slow.
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the executor.

        This includes all attached resources such as workers and controllers.
        """
        pass

    @abstractproperty
    def scaling_enabled(self) -> bool:
        """Specify if scaling is enabled.

        The callers of ParslExecutors need to differentiate between Executors
        and Executors wrapped in a resource provider
        """
        pass

    @property
    def run_dir(self) -> str:
        """Path to the run directory.
        """
        return self._run_dir

    @run_dir.setter
    def run_dir(self, value: str) -> None:
        self._run_dir = value

    @property
    def hub_address(self) -> Optional[str]:
        """Address to the Hub for monitoring.
        """
        return self._hub_address

    @hub_address.setter
    def hub_address(self, value: Optional[str]) -> None:
        self._hub_address = value

    @property
    def hub_port(self) -> Optional[int]:
        """Port to the Hub for monitoring.
        """
        return self._hub_port

    @hub_port.setter
    def hub_port(self, value: Optional[int]) -> None:
        self._hub_port = value
