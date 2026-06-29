from django.core.mail import send_mail


def _send(to_email, subject, body):
    if not to_email:
        return
    send_mail(
        subject=subject,
        message=body,
        from_email='no-reply@multilojas.local',
        recipient_list=[to_email],
        fail_silently=True,
    )


def notify_order_approved(order):
    _send(
        order.comprador.email,
        f'Pedido #{order.id} aprovado',
        f'O seu pedido #{order.id} foi aprovado pelo vendedor {order.loja.nome_loja}.',
    )


def notify_order_rejected(order):
    _send(
        order.comprador.email,
        f'Pedido #{order.id} rejeitado',
        f'O seu pedido #{order.id} foi rejeitado. Motivo: {order.rejection_reason or "não informado"}',
    )


def notify_order_shipped(order):
    _send(
        order.comprador.email,
        f'Pedido #{order.id} enviado',
        f'O seu pedido #{order.id} foi enviado. Código de rastreio: {order.tracking_code}.',
    )
