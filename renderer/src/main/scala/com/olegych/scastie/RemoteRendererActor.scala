package com.olegych.scastie

import akka.camel.{CamelMessage, Consumer, Producer}
import akka.actor.Actor
import akka.serialization.{JavaSerializer, SerializationExtension}
import java.io.{ByteArrayOutputStream, ByteArrayInputStream, InputStream}
import org.apache.camel.support.TypeConverterSupport
import org.apache.camel.Exchange
import org.apache.camel.CamelContext
import org.apache.camel.converter.stream.InputStreamCache


trait CamelSerialization extends Actor {
  def addSerialization(camelContext: CamelContext) {
    val ser = SerializationExtension(context.system)
    camelContext.getTypeConverterRegistry
        .addTypeConverter(classOf[InputStream], classOf[AnyRef], new TypeConverterSupport {
      def convertTo[T](tpe: Class[T], exchange: Exchange, value: Any) = tpe
          .cast(new ByteArrayInputStream(ser.serialize(value.asInstanceOf[AnyRef]).get))
    })
    camelContext.getTypeConverterRegistry
        .addTypeConverter(classOf[Product], classOf[InputStreamCache], new TypeConverterSupport {
      def convertTo[T](tpe: Class[T], exchange: Exchange, value: Any) = tpe
          .cast(ser.deserialize(getBytes(value.asInstanceOf[InputStreamCache]),
        new JavaSerializer(ser.system).identifier, None).get)

      def getBytes(is: InputStreamCache) = {
        val stream = new ByteArrayOutputStream()
        is.writeTo(stream)
        stream.toByteArray
      }
    })
  }
}

class RemoteRendererActor(url: String) extends Actor with Producer with CamelSerialization {
  addSerialization(camelContext)
  def endpointUri = s"jetty:http://$url"
}

class RemoteRendererActorServer(url: String) extends Actor with Consumer with CamelSerialization {
  addSerialization(camelContext)
  val renderer = ActorsHome.createRenderer(context, localOnly = true)
  def endpointUri = s"jetty:http://$url"
  def receive = {
    case m: CamelMessage => renderer forward m.bodyAs[Product]
  }
}
