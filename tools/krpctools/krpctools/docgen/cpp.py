from krpc.schema.KRPC import Type
from krpc.types import \
    ValueType, ClassType, EnumerationType, MessageType, \
    TupleType, ListType, SetType, DictionaryType
from krpc.utils import snake_case
from .domain import Domain
from .nodes import \
    Procedure, Property, Class, ClassMethod, ClassStaticMethod, \
    ClassProperty, Enumeration, EnumerationValue


class CppDomain(Domain):
    name = 'cpp'
    prettyname = 'C++'
    sphinxname = 'cpp'
    codeext = 'cpp'

    type_map = {
        Type.DOUBLE: 'double',
        Type.FLOAT: 'float',
        Type.SINT32: 'int32_t',
        Type.SINT64: 'int64_t',
        Type.UINT32: 'uint32_t',
        Type.UINT64: 'uint64_t',
        Type.BOOL: 'bool',
        Type.STRING: 'std::string',
        Type.BYTES: 'std::string'
    }

    value_map = {
        'null': 'NULL'
    }

    def __init__(self, macros):
        super(CppDomain, self).__init__(macros)

    def currentmodule(self, name):
        super(CppDomain, self).currentmodule(name)
        return '.. namespace:: krpc::services::%s' % name

    def type(self, typ):
        if typ is None:
            return 'void'
        elif isinstance(typ, ValueType):
            return self.type_map[typ.protobuf_type.code]
        elif isinstance(typ, MessageType):
            return 'krpc::schema::%s' % typ.python_type.__name__
        elif isinstance(typ, ClassType) or isinstance(typ, EnumerationType):
            name = '%s.%s' % \
                   (typ.protobuf_type.service, typ.protobuf_type.name)
            return self.shorten_ref(name).replace('.', '::')
        elif isinstance(typ, ListType):
            return 'std::vector<%s>' % self.type(typ.value_type)
        elif isinstance(typ, DictionaryType):
            return 'std::map<%s,%s>' % \
                (self.type(typ.key_type), self.type(typ.value_type))
        elif isinstance(typ, SetType):
            return 'std::set<%s>' % self.type(typ.value_type)
        elif isinstance(typ, TupleType):
            return 'std::tuple<%s>' % \
                ', '.join(self.type(typ) for typ in typ.value_types)
        else:
            raise RuntimeError('Unknown type \'%s\'' % str(typ))

    def type_description(self, typ):
        if typ is None:
            return 'void'
        elif isinstance(typ, ValueType):
            return self.type_map[typ.protobuf_type.code]
        elif isinstance(typ, MessageType):
            return ':class:`krpc::schema::%s`' % typ.python_type.__name__
        elif isinstance(typ, ClassType):
            return ':class:`%s`' % self.type(typ)
        elif isinstance(typ, EnumerationType):
            return ':class:`%s`' % self.type(typ)
        elif isinstance(typ, ListType):
            return 'std::vector<%s>' % self.type_description(typ.value_type)
        elif isinstance(typ, DictionaryType):
            return 'std::map<%s,%s>' % \
                (self.type_description(typ.key_type),
                 self.type_description(typ.value_type))
        elif isinstance(typ, SetType):
            return 'std::set<%s>' % self.type_description(typ.value_type)
        elif isinstance(typ, TupleType):
            return 'std::tuple<%s>' \
                % ', '.join(self.type_description(typ)
                            for typ in typ.value_types)
        else:
            raise RuntimeError('Unknown type \'%s\'' % str(typ))

    def ref(self, obj):
        name = obj.fullname.split('.')
        if any(isinstance(obj, cls) for cls in
               (Procedure, Property, ClassMethod, ClassStaticMethod,
                ClassProperty, EnumerationValue)):
            name[-1] = snake_case(name[-1])
        return self.shorten_ref('.'.join(name)).replace('.', '::')

    def see(self, obj):
        if isinstance(obj, Property) or isinstance(obj, ClassProperty):
            prefix = 'func'
        elif (isinstance(obj, Procedure) or
              isinstance(obj, ClassMethod) or
              isinstance(obj, ClassStaticMethod)):
            prefix = 'func'
        elif isinstance(obj, Class):
            prefix = 'class'
        elif isinstance(obj, Enumeration):
            prefix = 'enum'
        elif isinstance(obj, EnumerationValue):
            prefix = 'enumerator'
        else:
            raise RuntimeError(str(obj))
        return ':%s:`%s`' % (prefix, self.ref(obj))

    def paramref(self, name):
        return super(CppDomain, self).paramref(snake_case(name))

    def default_value(self, typ, value):
        if isinstance(typ, ValueType) and \
           typ.protobuf_type.code == Type.STRING:
            return '"%s"' % value
        if isinstance(typ, ValueType) and \
           typ.protobuf_type.code == Type.BOOL:
            if value:
                return 'true'
            else:
                return 'false'
        elif isinstance(typ, EnumerationType):
            return 'static_cast<%s>(%s)' % (self.type(typ), value)
        elif value is None:
            return self.type(typ) + '()'
        elif isinstance(typ, TupleType):
            values = (self.default_value(typ.value_types[i], x)
                      for i, x in enumerate(value))
            return '(%s)' % ', '.join(values)
        elif isinstance(typ, ListType):
            values = (self.default_value(typ.value_type, x) for x in value)
            return '(%s)' % ', '.join(values)
        elif isinstance(typ, SetType):
            values = (self.default_value(typ.value_type, x) for x in value)
            return '(%s)' % ', '.join(values)
        elif isinstance(typ, DictionaryType):
            entries = ('(%s, %s)' % (self.default_value(typ.key_type, k),
                                     self.default_value(typ.value_type, v))
                       for k, v in value.items())
            return '(%s)' % ', '.join(entries)
        else:
            return str(value)
