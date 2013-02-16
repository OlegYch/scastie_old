package com.olegych.scastie

import akka.actor._
import akka.routing.FromConfig
import util.Try
import com.typesafe.config.Config

/**
  */
object ActorsHome {

  def createRenderer(implicit context: ActorContext, localOnly: Boolean = false) = context.actorOf(
    props = httpEndpoint(context.system.settings.config)
        .filterNot(_ => localOnly)
        .map(url => Props(new RemoteRendererActor(url)))
        .getOrElse(Props[RendererActor].withRouter(FromConfig())),
    name = "renderer")

  def createServer(implicit context: ActorSystem) = context
      .actorOf(Props(new RemoteRendererActorServer(httpEndpoint(context.settings.config).get)), "server")

  def createFailures(implicit context: ActorContext) = context.actorOf(Props[FailuresActor], "failures")

  def httpEndpoint(config: Config) = Try(config.getString("akka.remote.httpEndpoint")).toOption
}
