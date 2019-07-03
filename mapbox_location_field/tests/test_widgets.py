from collections import OrderedDict

from django.test import TestCase
from django.conf import settings

from mapbox_location_field.widgets import MapInput


class MapInputTests(TestCase):

    def equality_of_random_javascript(self, outputed_string, expected_list):
        expected_list.append("")
        outputed_list = outputed_string.split(";")
        self.assertEqual(len(outputed_list), len(expected_list))
        for statement in expected_list:
            self.assertIn(statement, outputed_list)

    def test_map_attrs_defaults(self):
        widget = MapInput()
        self.assertEqual(widget.map_attrs, {})
        self.assertEqual(widget.placeholder, "Pick a location on map below")
        self.assertTrue(widget.readonly)

    def test_map_attrs_customized(self):
        widget = MapInput(map_attrs={"readonly": False, "placeholder": "location", "zoom": 14})
        self.assertEqual(widget.map_attrs, {"zoom": 14, })
        self.assertEqual(widget.placeholder, "location")
        self.assertFalse(widget.readonly)

    def test_get_contex(self):
        widget = MapInput(map_attrs={"readonly": False, "placeholder": "cool location field placeholder"})
        contex = widget.get_context("location_field", None,
                                    {"placeholder": "not cool location field placeholder", "readonly": True, })

        self.assertEqual(contex["widget"]["attrs"]["placeholder"], "cool location field placeholder")
        self.assertFalse(contex["widget"]["attrs"]["readonly"])
        self.assertTrue(contex["widget"]["attrs"]["class"].endswith(" js-mapbox-input-location-field"))

    def test_get_contex_when_map_attrs_None(self):
        widget = MapInput()
        contex = widget.get_context("location_field", None, None)
        self.assertEqual(contex["widget"]["attrs"]["placeholder"], "Pick a location on map below")
        self.assertTrue(contex["widget"]["attrs"]["readonly"])
        self.assertTrue(contex["widget"]["attrs"]["class"].endswith(" js-mapbox-input-location-field"))

    def test_map_attrs_to_javascript(self):
        widget = MapInput()
        map_attrs = {
            "list": [1, 2],
            "tuple": (1, 2),
            "bool": True,
            "string": "cool string",
            "int": 1,
            "float": 1.2,
        }

        javascript = widget.map_attrs_to_javascript(map_attrs)
        expected_js_list = ["var map_attr_list = [1, 2]", "var map_attr_tuple = [1, 2]", "var map_attr_bool = true",
                            "var map_attr_string = 'cool string'", "var map_attr_int = '1'",
                            "var map_attr_float = '1.2'"]
        self.equality_of_random_javascript(javascript, expected_js_list)

    def test_get_config_settings_defaults(self):
        widget = MapInput()
        settings.MAPBOX_KEY = "MY_COOL_MAPBOX_KEY"

        expected_js_list = ["var map_attr_style = 'mapbox://styles/mapbox/outdoors-v11'", "var map_attr_zoom = '13'",
                            "var map_attr_center = [17.031645, 51.106715]", "var map_attr_cursor_style = 'pointer'",
                            "var map_attr_marker_color = 'red'", "var map_attr_rotate = false",
                            "var map_attr_geocoder = true",
                            "var map_attr_fullscreen_button = true", "var map_attr_navigation_buttons = true",
                            "var map_attr_track_location_button = true"]

        result = widget.get_config_settings()
        self.assertTrue(result.startswith("<script>mapboxgl.accessToken = 'MY_COOL_MAPBOX_KEY';"))
        self.assertTrue(result.endswith("</script>"))
        crippled_result = result[52:-9]

        self.equality_of_random_javascript(crippled_result, expected_js_list)

    def test_get_config_settings_updated_with_map_attrs(self):
        widget = MapInput(map_attrs={
            "style": "cool style",
            "zoom": 90,
            "center": [1, 5.1],
            "cursor_style": 'cell',
            "marker_color": "blue",
            "rotate": True,
            "geocoder": False,
            "fullscreen_button": False,
            "navigation_buttons": False,
            "track_location_button": False, })

        settings.MAPBOX_KEY = "MY_COOL_MAPBOX_KEY"

        expected_js_list = ["var map_attr_style = 'cool style'", "var map_attr_zoom = '90'",
                            "var map_attr_center = [1, 5.1]", "var map_attr_cursor_style = 'cell'",
                            "var map_attr_marker_color = 'blue'", "var map_attr_rotate = true",
                            "var map_attr_geocoder = false",
                            "var map_attr_fullscreen_button = false", "var map_attr_navigation_buttons = false",
                            "var map_attr_track_location_button = false"]

        result = widget.get_config_settings()

        self.assertTrue(result.startswith("<script>mapboxgl.accessToken = 'MY_COOL_MAPBOX_KEY';"))
        self.assertTrue(result.endswith("</script>"))
        crippled_result = result[52:-9]

        self.equality_of_random_javascript(crippled_result, expected_js_list)

    def test_render(self):
        settings.MAPBOX_KEY = "MY_COOL_MAPBOX_KEY"
        attrs = {"maxlength": 63, "class": "form-group", "required": True, "id": "id_location", }
        attrs = OrderedDict(sorted(attrs.items(), key=lambda t: t[0]))
        widget = MapInput()
        expected_rend = '<input type="text" name="location" class="form-group js-mapbox-input-location-field" id="id_location" maxlength="63" required readonly placeholder="Pick a location on map below">\n\n' + "<div id='secret-id-map-mapbox-location-field' class='location-field-map'></div>\n<div id='secret-id-geocoder-mapbox-location-field' class='location-field-geocoder'></div><script>mapboxgl.accessToken = 'MY_COOL_MAPBOX_KEY';var map_attr_style = 'mapbox://styles/mapbox/outdoors-v11';var map_attr_zoom = '13';var map_attr_center = [17.031645, 51.106715];var map_attr_cursor_style = 'pointer';var map_attr_marker_color = 'red';var map_attr_rotate = false;var map_attr_geocoder = true;var map_attr_fullscreen_button = true;var map_attr_navigation_buttons = true;var map_attr_track_location_button = true;</script>"
        rend = widget.render("location", None, attrs=attrs)
        self.maxDiff = None

        self.assertEqual(rend, expected_rend)
