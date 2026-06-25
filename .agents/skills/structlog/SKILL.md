---
name: structlog
description: Provides specialized context, rules, and tools for implementing, configuring, and debugging structlog. Use this skill whenever modifying structlog configurations or adding related functionality.
---
# structlog

## File Tree

```text
structlog/
├── assets
├── modules
│   └── structlog (See AST Map below)
├── references
├── scripts
└── SKILL.md
```

> **Agent Instructions:** The AST maps below provide a high-level overview of the `modules/` directory. Note that the complete repository source code is available within the `modules/` folder. You can and should use your file reading tools to access the actual source code within `modules/` for complete details, implementation logic, and context beyond what the AST map provides.

### AST Map: `modules/structlog`

```python
show_off.py:
⋮
│@dataclass
│class SomeClass:
⋮
│def make_call_stack_more_impressive():
⋮

src\structlog\__init__.py:
⋮
│def __getattr__(name: str) -> str:
⋮

src\structlog\_base.py:
⋮
│class BoundLoggerBase:
│    """
│    Immutable context carrier.
│
│    Doesn't do any actual logging; examples for useful subclasses are:
│
│    - the generic `BoundLogger` that can wrap anything,
│    - `structlog.stdlib.BoundLogger`.
│    - `structlog.twisted.BoundLogger`,
│
│    See also `custom-wrappers`.
⋮
│    def __repr__(self) -> str:
⋮
│    def __eq__(self, other: object) -> bool:
⋮
│    def __ne__(self, other: object) -> bool:
⋮
│    def bind(self, **new_values: Any) -> Self:
⋮
│    def unbind(self, *keys: str) -> Self:
⋮
│    def try_unbind(self, *keys: str) -> Self:
⋮
│    def new(self, **new_values: Any) -> Self:
⋮
│    def _process_event(
│        self, method_name: str, event: str | None, event_kw: dict[str, Any]
⋮
│    def _proxy_to_logger(
│        self, method_name: str, event: str | None = None, **event_kw: Any
⋮
│def get_context(bound_logger: BindableLogger) -> Context:
⋮

src\structlog\_config.py:
⋮
│class _Configuration:
⋮
│def is_configured() -> bool:
⋮
│def get_config() -> dict[str, Any]:
⋮
│def get_logger(*args: Any, **initial_values: Any) -> Any:
⋮
│def wrap_logger(
│    logger: WrappedLogger | None,
│    processors: Iterable[Processor] | None = None,
│    wrapper_class: type[BindableLogger] | None = None,
│    context_class: type[Context] | None = None,
│    cache_logger_on_first_use: bool | None = None,
│    logger_factory_args: Iterable[Any] | None = None,
│    **initial_values: Any,
⋮
│def configure(
│    processors: Iterable[Processor] | None = None,
│    wrapper_class: type[BindableLogger] | None = None,
│    context_class: type[Context] | None = None,
│    logger_factory: Callable[..., WrappedLogger] | None = None,
│    cache_logger_on_first_use: bool | None = None,
⋮
│def configure_once(
│    processors: Iterable[Processor] | None = None,
│    wrapper_class: type[BindableLogger] | None = None,
│    context_class: type[Context] | None = None,
│    logger_factory: Callable[..., WrappedLogger] | None = None,
│    cache_logger_on_first_use: bool | None = None,
⋮
│def reset_defaults() -> None:
⋮
│class BoundLoggerLazyProxy:
│    """
│    Instantiates a bound logger on first usage.
│
│    Takes both configuration and instantiation parameters into account.
│
│    The only points where a bound logger changes state are ``bind()``,
│    ``unbind()``, and ``new()`` and that return the actual ``BoundLogger``.
│
│    If and only if configuration says so, that actual bound logger is cached on
│    first usage.
│
⋮
│    @property
│    def _context(self) -> dict[str, str]:
⋮
│    def bind(self, **new_values: Any) -> BindableLogger:
│        """
│        Assemble a new BoundLogger from arguments and configuration.
⋮
│        def finalized_bind(**new_values: Any) -> BindableLogger:
⋮
│    def unbind(self, *keys: str) -> BindableLogger:
⋮
│    def try_unbind(self, *keys: str) -> BindableLogger:
⋮
│    def new(self, **new_values: Any) -> BindableLogger:
⋮

src\structlog\_frames.py:
⋮
│def _format_exception(exc_info: ExcInfo) -> str:
⋮
│def _find_first_app_frame_and_name(
│    additional_ignores: list[str] | None = None,
│    *,
│    stacklevel: int | None = None,
│    _getframe: Callable[[], FrameType] = sys._getframe,
⋮
│def _format_stack(frame: FrameType) -> str:
⋮

src\structlog\_generic.py:
⋮
│class BoundLogger(BoundLoggerBase):
│    """
│    A generic BoundLogger that can wrap anything.
│
│    Every unknown method will be passed to the wrapped *logger*. If that's too
│    much magic for you, try `structlog.stdlib.BoundLogger` or
│    `structlog.twisted.BoundLogger` which also take advantage of knowing the
│    wrapped class which generally results in better performance.
│
│    Not intended to be instantiated by yourself.  See
│    :func:`~structlog.wrap_logger` and :func:`~structlog.get_logger`.
⋮
│    def __getattr__(self, method_name: str) -> Any:
⋮
│    def __getstate__(self) -> dict[str, Any]:
⋮

src\structlog\_greenlets.py:
⋮
│class GreenThreadLocal:
│    """
│    threading.local() replacement for greenlets.
⋮
│    def __getattr__(self, name: str) -> Any:
⋮
│    def __setattr__(self, name: str, val: Any) -> None:
⋮

src\structlog\_log_levels.py:
⋮
│def map_method_name(method_name: str) -> str:
⋮

src\structlog\_native.py:
⋮
│def exception(
│    self: FilteringBoundLogger, event: str, *args: Any, **kw: Any
⋮
│async def aexception(
│    self: FilteringBoundLogger, event: str, *args: Any, **kw: Any
⋮
│def make_filtering_bound_logger(
│    min_level: int | str,
⋮
│def _maybe_interpolate(event: str, args: tuple[Any, ...]) -> str:
⋮
│def _make_filtering_bound_logger(min_level: int) -> type[FilteringBoundLogger]:
│    """
│    Create a new `FilteringBoundLogger` that only logs *min_level* or higher.
│
│    The logger is optimized such that log levels below *min_level* only consist
│    of a ``return None``.
⋮
│    def make_method(
│        level: int,
│    ) -> tuple[Callable[..., Any], Callable[..., Any]]:
│        if level < min_level:
⋮
│        def meth(self: Any, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def log(self: Any, level: int, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def alog(
│        self: Any, level: int, event: str, *args: Any, **kw: Any
⋮

src\structlog\_output.py:
⋮
│def _get_lock_for_file(file: IO[Any]) -> threading.Lock:
⋮
│class PrintLogger:
│    """
│    Print events into a file.
│
│    Args:
│        file: File to print to. (default: `sys.stdout`)
│
│    >>> from structlog import PrintLogger
│    >>> PrintLogger().info("hello")
│    hello
│
⋮
│    def __getstate__(self) -> str:
⋮
│    def __repr__(self) -> str:
⋮
│    def msg(self, message: str) -> None:
⋮
│class PrintLoggerFactory:
⋮
│class WriteLogger:
│    """
│    Write events into a file.
│
│    Args:
│        file: File to print to. (default: `sys.stdout`)
│
│    >>> from structlog import WriteLogger
│    >>> WriteLogger().info("hello")
│    hello
│
⋮
│    def __repr__(self) -> str:
⋮
│    def msg(self, message: str) -> None:
⋮
│class WriteLoggerFactory:
⋮
│class BytesLogger:
│    r"""
│    Writes bytes into a file.
│
│    Useful if you follow `current logging best practices
│    <logging-best-practices>` together with a formatter that returns bytes
│    (e.g. `orjson <https://github.com/ijl/orjson>`_).
│
│    Args:
│        file: File to print to. (default: `sys.stdout`\ ``.buffer``)
│
⋮
│    def __repr__(self) -> str:
⋮
│    def msg(self, message: bytes) -> None:
⋮
│class BytesLoggerFactory:
⋮

src\structlog\_utils.py:
⋮
│def get_processname() -> str:
⋮

src\structlog\contextvars.py:
⋮
│def get_contextvars() -> dict[str, Any]:
⋮
│def get_merged_contextvars(bound_logger: BindableLogger) -> dict[str, Any]:
⋮
│def merge_contextvars(
│    logger: WrappedLogger, method_name: str, event_dict: EventDict
⋮
│def clear_contextvars() -> None:
⋮
│def bind_contextvars(**kw: Any) -> Mapping[str, contextvars.Token[Any]]:
⋮
│def reset_contextvars(**kw: contextvars.Token[Any]) -> None:
⋮
│def unbind_contextvars(*keys: str) -> None:
⋮
│@contextlib.contextmanager
│def bound_contextvars(**kw: Any) -> Generator[None, None, None]:
⋮

src\structlog\dev.py:
⋮
│if _IS_WINDOWS:  # pragma: no cover
│
│    def _init_terminal(who: str, force_colors: bool) -> None:
│        """
│        Initialize colorama on Windows systems for colorful console output.
│
│        Args:
│            who: The name of the caller for error messages.
│
│            force_colors:
│                Force colorful output even in non-interactive environments.
│
⋮
│else:
│
│    def _init_terminal(who: str, force_colors: bool) -> None:
│        """
│        Currently, nothing to be done on non-Windows systems.
⋮
│@dataclass(frozen=True)
│class ColumnStyles:
⋮
│@dataclass
│class Column:
⋮
│@dataclass
│class KeyValueColumnFormatter:
⋮
│class LogLevelColumnFormatter:
⋮
│@dataclass
│class RichTracebackFormatter:
⋮
│if rich is None:
│
│    def rich_traceback(*args, **kw):
│        raise ModuleNotFoundError(
│            "RichTracebackFormatter requires Rich to be installed.",
│            name="rich",
⋮
│def better_traceback(sio: TextIO, exc_info: ExcInfo) -> None:
⋮
│class ConsoleRenderer:
│    r"""
│    Render ``event_dict`` nicely aligned, possibly in colors, and ordered.
│
│    If ``event_dict`` contains a true-ish ``exc_info`` key, it will be rendered
│    *after* the log line. If Rich_ is present, in colors and with extra
│    context.
│
│    Tip:
│        Since `ConsoleRenderer` is mainly a development helper, it is less
│        strict about immutability than the rest of *structlog* for better
⋮
│    def __init__(
│        self,
│        pad_event_to: int = _EVENT_WIDTH,
│        colors: bool = _has_colors,
│        force_colors: bool = False,
│        repr_native_str: bool = False,
│        level_styles: dict[str, str] | None = None,
│        exception_formatter: ExceptionRenderer = default_exception_formatter,
│        sort_keys: bool = True,
│        event_key: str = "event",
⋮
│        if pad_event is not None:
│            if pad_event_to != _EVENT_WIDTH:
│                raise ValueError(
│                    "Cannot set both `pad_event` and `pad_event_to`."
│                )
│            warnings.warn(
│                "The `pad_event` argument is deprecated. Use `pad_event_to` instead.",
│                DeprecationWarning,
│                stacklevel=2,
│            )
⋮
│        def add_meaningless_arg(arg: str) -> None:
⋮
│    @classmethod
│    def get_active(cls) -> ConsoleRenderer:
⋮
│    @classmethod
│    def get_default_column_styles(
│        cls, colors: bool, force_colors: bool = False
⋮
│    @staticmethod
│    def get_default_level_styles(colors: bool = True) -> dict[str, str]:
⋮
│    def _configure_columns(self) -> None:
⋮
│def set_exc_info(
│    logger: WrappedLogger, method_name: str, event_dict: EventDict
⋮

src\structlog\exceptions.py:
⋮
│class DropEvent(BaseException):
⋮
│class NoConsoleRendererConfiguredError(Exception):
⋮
│class MultipleConsoleRenderersConfiguredError(Exception):
⋮

src\structlog\processors.py:
⋮
│class KeyValueRenderer:
⋮
│class LogfmtRenderer:
⋮
│def _items_sorter(
│    sort_keys: bool,
│    key_order: Sequence[str] | None,
│    drop_missing: bool,
⋮
│class UnicodeEncoder:
⋮
│class UnicodeDecoder:
⋮
│class JSONRenderer:
⋮
│class ExceptionRenderer:
⋮
│class TimeStamper:
⋮
│def _make_stamper(
│    fmt: str | None, utc: bool, key: str
│) -> Callable[[EventDict], EventDict]:
│    """
│    Create a stamper function.
⋮
│    if utc:
│
│        def now() -> datetime.datetime:
⋮
│    else:
│
│        def now() -> datetime.datetime:
│            # We don't need the TZ for our own formatting. We add it only for
│            # user-defined formats later.
⋮
│class MaybeTimeStamper:
⋮
│def _figure_out_exc_info(v: Any) -> ExcInfo | None:
⋮
│class ExceptionPrettyPrinter:
⋮
│class StackInfoRenderer:
⋮
│class CallsiteParameterAdder:
│    """
│    Adds parameters of the callsite that an event dictionary originated from to
│    the event dictionary. This processor can be used to enrich events
│    dictionaries with information such as the function name, line number and
│    filename that an event dictionary originated from.
│
│    If the event dictionary has an embedded `logging.LogRecord` object and did
│    not originate from *structlog* then the callsite information will be
│    determined from the `logging.LogRecord` object. For event dictionaries
│    without an embedded `logging.LogRecord` object the callsite will be
⋮
│    class _RecordMapping(NamedTuple):
⋮
│class EventRenamer:
⋮

src\structlog\stdlib.py:
⋮
│def recreate_defaults(*, log_level: int | None = logging.NOTSET) -> None:
⋮
│class _FixedFindCallerLogger(logging.Logger):
│    """
│    Change the behavior of `logging.Logger.findCaller` to cope with
│    *structlog*'s extra frames.
⋮
│    def findCaller(
│        self, stack_info: bool = False, stacklevel: int = 1
⋮
│class BoundLogger(BoundLoggerBase):
│    """
│    Python Standard Library version of `structlog.BoundLogger`.
│
│    Works exactly like the generic one except that it takes advantage of
│    knowing the logging methods in advance.
│
│    Use it like::
│
│        structlog.configure(
│            wrapper_class=structlog.stdlib.BoundLogger,
⋮
│    def bind(self, **new_values: Any) -> Self:
⋮
│    def unbind(self, *keys: str) -> Self:
⋮
│    def try_unbind(self, *keys: str) -> Self:
⋮
│    def new(self, **new_values: Any) -> Self:
⋮
│    def debug(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def info(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def warning(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def error(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def critical(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def fatal(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
⋮
│    def exception(
│        self, event: str | None = None, *args: Any, **kw: Any
⋮
│    def log(
│        self, level: int, event: str | None = None, *args: Any, **kw: Any
⋮
│    def _proxy_to_logger(
│        self,
│        method_name: str,
│        event: str | None = None,
│        *event_args: str,
│        **event_kw: Any,
⋮
│    @property
│    def level(self) -> int:
⋮
│    def setLevel(self, level: int) -> None:
⋮
│    def findCaller(
│        self, stack_info: bool = False, stacklevel: int = 1
⋮
│    def makeRecord(
│        self,
│        name: str,
│        level: int,
│        fn: str,
│        lno: int,
│        msg: str,
│        args: tuple[Any, ...],
│        exc_info: ExcInfo,
│        func: str | None = None,
⋮
│    def handle(self, record: logging.LogRecord) -> None:
⋮
│    def addHandler(self, hdlr: logging.Handler) -> None:
⋮
│    def removeHandler(self, hdlr: logging.Handler) -> None:
⋮
│    def hasHandlers(self) -> bool:
⋮
│    def callHandlers(self, record: logging.LogRecord) -> None:
⋮
│    def getEffectiveLevel(self) -> int:
⋮
│    def isEnabledFor(self, level: int) -> bool:
⋮
│    def is_enabled_for(self, level: int) -> bool:
⋮
│    def get_effective_level(self) -> int:
⋮
│    def getChild(self, suffix: str) -> logging.Logger:
⋮
│    async def _dispatch_to_sync(
│        self,
│        meth: Callable[..., Any],
│        event: str,
│        args: tuple[Any, ...],
│        kw: dict[str, Any],
⋮
│    async def adebug(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def ainfo(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def awarning(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def aerror(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def acritical(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def afatal(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def aexception(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def alog(
│        self, level: Any, event: str, *args: Any, **kw: Any
⋮
│def get_logger(*args: Any, **initial_values: Any) -> BoundLogger:
⋮
│class AsyncBoundLogger:
│    """
│    Wraps a `BoundLogger` & exposes its logging methods as ``async`` versions.
│
│    This approach has turned out to be a mistake and the class has been
│    deprecated in 23.1.0. Use the regular `BoundLogger` with its a-prefixed
│    methods instead.
│
│    .. versionadded:: 20.2.0
│    .. versionchanged:: 20.2.0 fix _dispatch_to_sync contextvars usage
│    .. deprecated:: 23.1.0
⋮
│    @property
│    def _context(self) -> Context:
⋮
│    def bind(self, **new_values: Any) -> Self:
⋮
│    def new(self, **new_values: Any) -> Self:
⋮
│    def unbind(self, *keys: str) -> Self:
⋮
│    def try_unbind(self, *keys: str) -> Self:
⋮
│    async def _dispatch_to_sync(
│        self,
│        meth: Callable[..., Any],
│        event: str,
│        args: tuple[Any, ...],
│        kw: dict[str, Any],
⋮
│    async def debug(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def info(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def warning(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def warn(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def error(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def critical(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def fatal(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def exception(self, event: str, *args: Any, **kw: Any) -> None:
⋮
│    async def log(self, level: Any, event: str, *args: Any, **kw: Any) -> None:
⋮
│class LoggerFactory:
⋮
│class PositionalArgumentsFormatter:
⋮
│class ExtraAdder:
⋮
│class ProcessorFormatter(logging.Formatter):
│    r"""
│    Call *structlog* processors on `logging.LogRecord`\s.
│
│    This is an implementation of a `logging.Formatter` that can be used to
│    format log entries from both *structlog* and `logging`.
│
│    Its static method `wrap_for_formatter` must be the final processor in
│    *structlog*'s processor chain.
│
│    Please refer to :ref:`processor-formatter` for examples.
│
⋮
│    def format(self, record: logging.LogRecord) -> str:
⋮

src\structlog\testing.py:
⋮
│class LogCapture:
⋮
│@contextmanager
│def capture_logs(
│    processors: Iterable[Processor] = (),
⋮
│class ReturnLogger:
│    """
│    Return the arguments that it's called with.
│
│    >>> from structlog import ReturnLogger
│    >>> ReturnLogger().info("hello")
│    'hello'
│    >>> ReturnLogger().info("hello", when="again")
│    (('hello',), {'when': 'again'})
│
│    .. versionchanged:: 0.3.0
⋮
│    def msg(self, *args: Any, **kw: Any) -> Any:
⋮
│class ReturnLoggerFactory:
⋮
│class CapturedCall(NamedTuple):
⋮
│class CapturingLogger:
│    """
│    Store the method calls that it's been called with.
│
│    This is nicer than `ReturnLogger` for unit tests because the bound logger
│    doesn't have to cooperate.
│
│    **Any** method name is supported.
│
│    .. versionadded:: 20.2.0
⋮
│    def __getattr__(self, name: str) -> Any:
│        """
│        Capture call to `calls`
⋮
│        def log(*args: Any, **kw: Any) -> None:
⋮
│class CapturingLoggerFactory:
⋮

src\structlog\threadlocal.py:
⋮
│def _determine_threadlocal() -> type[Any]:
⋮
│def _deprecated() -> None:
⋮
│def wrap_dict(dict_class: type[Context]) -> type[Context]:
⋮
│def as_immutable(logger: TLLogger) -> TLLogger:
⋮
│@contextlib.contextmanager
│def tmp_bind(
│    logger: TLLogger, **tmp_values: Any
⋮
│class _ThreadLocalDictWrapper:
│    """
│    Wrap a dict-like class and keep the state *global* but *thread-local*.
│
│    Attempts to re-initialize only updates the wrapped dictionary.
│
│    Useful for short-lived threaded applications like requests in web app.
│
│    Use :func:`wrap` to instantiate and use
│    :func:`structlog.BoundLogger.new` to clear the context.
⋮
│    def __eq__(self, other: object) -> bool:
⋮
│    def __iter__(self) -> Iterator[str]:
⋮
│    def __delitem__(self, key: str) -> None:
⋮
│def get_threadlocal() -> Context:
⋮
│def get_merged_threadlocal(bound_logger: BindableLogger) -> Context:
⋮
│def merge_threadlocal(
│    logger: WrappedLogger, method_name: str, event_dict: EventDict
⋮
│def clear_threadlocal() -> None:
⋮
│def bind_threadlocal(**kw: Any) -> None:
⋮
│def unbind_threadlocal(*keys: str) -> None:
⋮
│@contextlib.contextmanager
│def bound_threadlocal(**kw: Any) -> Generator[None, None, None]:
⋮
│def _get_context() -> Context:
⋮

src\structlog\tracebacks.py:
⋮
│@dataclass
│class Frame:
⋮
│@dataclass
│class SyntaxError_:  # noqa: N801
⋮
│@dataclass
│class Stack:
⋮
│@dataclass
│class Trace:
⋮
│def safe_str(_object: Any) -> str:
⋮
│def to_repr(
│    obj: Any,
│    max_length: int | None = None,
│    max_string: int | None = None,
│    use_rich: bool = True,
⋮
│def extract(
│    exc_type: type[BaseException],
│    exc_value: BaseException,
│    traceback: TracebackType | None,
│    *,
│    show_locals: bool = False,
│    locals_max_length: int = LOCALS_MAX_LENGTH,
│    locals_max_string: int = LOCALS_MAX_STRING,
│    locals_hide_dunder: bool = True,
│    locals_hide_sunder: bool = False,
⋮
│    """
│    Extract traceback information.
│
│    Args:
│        exc_type: Exception type.
│
│        exc_value: Exception value.
│
│        traceback: Python Traceback object.
│
⋮
│    while True:
│        exc_id = id(exc_value)
⋮
│        def get_locals(
│            iter_locals: Iterable[tuple[str, object]],
⋮
│class ExceptionDictTransformer:
│    """
│    Return a list of exception stack dictionaries for an exception.
│
│    These dictionaries are based on :class:`Stack` instances generated by
│    :func:`extract()` and can be dumped to JSON.
│
│    Args:
│        show_locals:
│            Whether or not to include the values of a stack frame's local
│            variables.
│
⋮
│    def _as_dict(self, trace: Trace) -> list[dict[str, Any]]:
⋮

src\structlog\twisted.py:
⋮
│class BoundLogger(BoundLoggerBase):
│    """
│    Twisted-specific version of `structlog.BoundLogger`.
│
│    Works exactly like the generic one except that it takes advantage of
│    knowing the logging methods in advance.
│
│    Use it like::
│
│        configure(
│            wrapper_class=structlog.twisted.BoundLogger,
⋮
│    def msg(self, event: str | None = None, **kw: Any) -> Any:
⋮
│    def err(self, event: str | None = None, **kw: Any) -> Any:
⋮
│class LoggerFactory:
⋮
│def _extractStuffAndWhy(eventDict: EventDict) -> tuple[Any, Any, EventDict]:
⋮
│class ReprWrapper:
│    """
│    Wrap a string and return it as the ``__repr__``.
│
│    This is needed for ``twisted.python.log.err`` that calls `repr` on
│    ``_stuff``:
│
│    >>> repr("foo")
│    "'foo'"
│    >>> repr(ReprWrapper("foo"))
│    'foo'
│
⋮
│    def __eq__(self, other: object) -> bool:
⋮
│class JSONRenderer(GenericJSONRenderer):
⋮
│@implementer(ILogObserver)
│class PlainFileLogObserver:
⋮
│@implementer(ILogObserver)
│class JSONLogObserverWrapper:
⋮
│def plainJSONStdOutLogger() -> JSONLogObserverWrapper:
⋮
│class EventAdapter:
⋮

src\structlog\typing.py:
⋮
│@runtime_checkable
│class ExceptionTransformer(Protocol):
⋮
│@runtime_checkable
│class BindableLogger(Protocol):
│    """
│    **Protocol**: Methods shared among all bound loggers and that are relied on
│    by *structlog*.
│
│    .. versionadded:: 20.2.0
⋮
│    @property
│    def _context(self) -> Context: ...
│
│    def bind(self, **new_values: Any) -> Self: ...
│
│    def unbind(self, *keys: str) -> Self: ...
│
│    def try_unbind(self, *keys: str) -> Self: ...
│
│    def new(self, **new_values: Any) -> Self: ...
│
⋮
│class FilteringBoundLogger(BindableLogger, Protocol):
│    """
│    **Protocol**: A `BindableLogger` that filters by a level.
│
│    The only way to instantiate one is using `make_filtering_bound_logger`.
│
│    .. versionadded:: 20.2.0
│    .. versionadded:: 22.2.0 String interpolation using positional arguments.
│    .. versionadded:: 22.2.0
│       Async variants ``alog()``, ``adebug()``, ``ainfo()``, and so forth.
│    .. versionchanged:: 22.3.0
⋮
│    def bind(self, **new_values: Any) -> FilteringBoundLogger:
⋮
│    def unbind(self, *keys: str) -> FilteringBoundLogger:
⋮
│    def try_unbind(self, *keys: str) -> FilteringBoundLogger:
⋮
│    def new(self, **new_values: Any) -> FilteringBoundLogger:
⋮
│    def is_enabled_for(self, level: int) -> bool:
⋮
│    def get_effective_level(self) -> int:
⋮
│    def debug(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def adebug(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def info(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def ainfo(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def warning(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def awarning(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def warn(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def awarn(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def error(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def aerror(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def err(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def fatal(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def afatal(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def exception(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def aexception(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def critical(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def acritical(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def msg(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def amsg(self, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    def log(self, level: int, event: str, *args: Any, **kw: Any) -> Any:
⋮
│    async def alog(self, level: int, event: str, *args: Any, **kw: Any) -> Any:
⋮

tests\additional_frame.py:
⋮
│def additional_frame(callable):
⋮

tests\conftest.py:
⋮
│@pytest.fixture(name="event_dict")
│def _event_dict():
│    """
│    An example event dictionary with multiple value types w/o the event itself.
⋮
│    class A:
⋮

tests\helpers.py:
⋮
│class CustomError(Exception):
⋮
│def stub(**kwargs):
⋮
│def call_recorder(func):
⋮

tests\processors\test_processors.py:
⋮
│class TestExceptionPrettyPrinter:
│    def test_stdout_by_default(self):
│        """
│        If no file is supplied, use stdout.
│        """
│        epp = ExceptionPrettyPrinter()
│
⋮
│    def test_uses_exception_formatter(self, sio):
│        """
│        If an `exception_formatter` is passed, use that to render the
│        exception rather than the default.
⋮
│        def formatter(exc_info: ExcInfo) -> str:
⋮
│class TestCallsiteParameterAdder:
│    parameter_strings = {
│        "pathname",
│        "filename",
│        "module",
│        "func_name",
│        "lineno",
│        "thread",
│        "thread_name",
│        "process",
│        "process_name",
⋮
│    @classmethod
│    def make_processor(
│        cls,
│        parameter_strings: set[str] | None,
│        additional_ignores: list[str] | None = None,
⋮
│    @classmethod
│    def filter_parameters(
│        cls, parameter_strings: set[str] | None
⋮
│    @classmethod
│    def filter_parameter_dict(
│        cls, input: dict[str, object], parameter_strings: set[str] | None
⋮
│    @classmethod
│    def get_callsite_parameters(cls, offset: int = 1) -> dict[str, object]:
⋮

tests\test_base.py:
⋮
│def build_bl(logger=None, processors=None, context=None):
⋮

tests\test_config.py:
⋮
│class TestBoundLoggerLazyProxy:
│    def test_repr(self):
│        """
│        repr reflects all attributes.
│        """
│        p = BoundLoggerLazyProxy(
│            None,
│            processors=[1, 2, 3],
│            context_class=dict,
│            initial_values={"foo": 42},
│            logger_factory_args=(4, 5),
⋮
│    def test_prefers_args_over_config(self):
│        """
│        Configuration can be overridden by passing arguments.
⋮
│        class Class:
│            def __init__(self, *args, **kw):
⋮
│            def update(self, *args, **kw):
⋮
│    def test_bind_doesnt_cache_logger(self):
│        """
│        Calling configure() changes BoundLoggerLazyProxys immediately.
│        Previous uses of the BoundLoggerLazyProxy don't interfere.
⋮
│        class F:
│            "New logger factory with a new attribute"
│
│            def info(self, *args):
⋮

tests\test_contextvars.py:
⋮
│class TestContextvars:
│    async def test_bind(self):
│        """
│        Binding a variable causes it to be included in the result of
│        merge_contextvars.
│        """
│        event_loop = asyncio.get_running_loop()
│
│        async def coro():
│            bind_contextvars(a=1)
│            return merge_contextvars(None, None, {"b": 2})
│
⋮
│    async def test_reset(self):
│        """
│        reset_contextvars allows resetting contexvars to
│        previously-set values.
⋮
│        async def nested_coro():
⋮
│    async def test_nested_async_bind(self):
│        """
│        Context is passed correctly between "nested" concurrent operations.
⋮
│        async def nested_coro():
⋮

tests\test_frames.py:
⋮
│class TestFindFirstAppFrameAndName:
│    def test_ignores_structlog_by_default(self):
│        """
│        No matter what you pass in, structlog frames get always ignored.
│        """
│        f1 = stub(f_globals={"__name__": "test"}, f_back=None)
│        f2 = stub(f_globals={"__name__": "structlog.blubb"}, f_back=f1)
│
│        f, n = _find_first_app_frame_and_name(_getframe=lambda: f2)
│
⋮
│    def test_ignoring_of_additional_frame_names_works(self):
⋮
│    def test_stacklevel(self):
⋮
│    def test_stacklevel_capped(self):
⋮
│    def test_tolerates_missing_name(self):
⋮
│    def test_tolerates_name_explicitly_None_oneframe(self):
⋮
│    def test_tolerates_name_explicitly_None_manyframe(self):
⋮
│    def test_tolerates_f_back_is_None(self):
⋮
│@pytest.fixture
│def exc_info():
⋮
│class TestFormatException:
│    def test_returns_str(self, exc_info):
│        """
│        Always returns a native string.
│        """
⋮
│    def test_formats(self, exc_info):
⋮
│    def test_no_trailing_nl(self, exc_info, monkeypatch):
⋮
│class TestFormatStack:
│    def test_returns_str(self):
│        """
│        Always returns a native string.
│        """
⋮
│    def test_formats(self):
⋮
│    def test_no_trailing_nl(self, monkeypatch):
⋮

tests\test_generic.py:
⋮
│class TestLogger:
│    def log(self, msg):
⋮

tests\test_packaging.py:
⋮
│class TestLegacyMetadataHack:
│    def test_version(self, recwarn):
│        """
│        structlog.__version__ returns the correct version and doesn't warn.
│        """
│        assert metadata.version("structlog") == structlog.__version__
⋮
│    def test_description(self):
⋮
│    def test_uri(self):
⋮
│    def test_email(self):
⋮
│    def test_does_not_exist(self):
⋮

tests\test_stdlib.py:
⋮
│def build_bl(logger=None, processors=None, context=None):
⋮
│def configure_logging(
│    pre_chain,
│    logger=None,
│    pass_foreign_args=False,
│    renderer=ConsoleRenderer(colors=False),  # noqa: B008
⋮

tests\test_testing.py:
⋮
│class TestCaptureLogs:
│    def test_captures_logs(self):
│        """
│        Log entries are captured and retain their structure.
│        """
│        with testing.capture_logs() as logs:
│            get_logger().bind(x="y").info("hello", answer=42)
│            get_logger().bind(a="b").info("goodbye", foo={"bar": "baz"})
│        assert [
│            {"event": "hello", "log_level": "info", "x": "y", "answer": 42},
│            {
⋮
│    def get_active_procs(self):
⋮

tests\test_threadlocal.py:
⋮
│class TestThreadLocalDict:
│    def test_wrap_returns_distinct_classes(self):
│        """
│        Each call to wrap_dict returns a distinct new class whose context is
│        independent from others.
│        """
│        with pytest.deprecated_call():
│            D1 = wrap_dict(dict)
│            D2 = wrap_dict(dict)
│
│        assert D1 != D2
⋮
│    @pytest.mark.skipif(
│        greenlet is not None, reason="Don't mix threads and greenlets."
│    )
│    def test_is_thread_local(self, D):
│        """
│        The context is *not* shared between threads.
⋮
│        class TestThread(threading.Thread):
│            def __init__(self, d):
│                self._d = d
⋮
│            def run(self):
⋮
│    @pytest.mark.skipif(greenlet is None, reason="Needs greenlet.")
│    def test_is_greenlet_local(self, D):
│        """
│        Context is shared between greenlets.
⋮
│        def run():
⋮

tests\test_tracebacks.py:
⋮
│class SecretStr(str):  # noqa: SLOT000
⋮
│def get_next_lineno() -> int:
⋮

tests\test_twisted.py:
⋮
│def build_bl(logger=None, processors=None, context=None):
⋮
```
