"""Сущность «Сводка по заказу» — данные для отображения на рабочем столе."""


class OrderSummary:
    def __init__(self, order_id, number, order_date, buyer, material_cost):
        self.id = order_id
        self.number = number
        self.order_date = order_date
        self.buyer = buyer
        self.material_cost = material_cost or 0.0

    @property
    def material_cost_text(self):
        return "{0:.2f}".format(self.material_cost)
