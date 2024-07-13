var map
document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('map')) {
        ymaps.ready(init).then( () => {

                                setTimeout(function () {
            map.container.fitToViewport();
            map.container.enterFullscreen(); // Выйти и войти в полноэкранный режим
            setTimeout(function () {
                map.container.exitFullscreen();
            }, 1);
        }, 1);
            }

        )
    }

    function init() {
        var startLat = parseFloatOrDefault(document.getElementById('id_start_location_latitude').value, null);
        var startLon = parseFloatOrDefault(document.getElementById('id_start_location_longitude').value, null);
        var endLat = parseFloatOrDefault(document.getElementById('id_end_location_latitude').value, null);
        var endLon = parseFloatOrDefault(document.getElementById('id_end_location_longitude').value, null);
        var currentLat = parseFloatOrDefault(document.getElementById('id_current_location_latitude').value, null);
        var currentLon = parseFloatOrDefault(document.getElementById('id_current_location_longitude').value, null);

        // Установим размеры карты
        var mapContainer = document.getElementById('map');
        mapContainer.style.width = '100%';
        mapContainer.style.height = '400px';

        map = new ymaps.Map("map", {
            center: [55.76, 37.64],
            zoom: 17
        });

        var startPoint = [startLat, startLon];
        var endPoint = [endLat, endLon];
        if ([startLat, startLon, endLat, endLon].some(coord => coord === null)) {
            return;
        }
        map.geoObjects.add(new ymaps.Placemark(startPoint, {balloonContent: 'Начальная точка'}));
        map.geoObjects.add(new ymaps.Placemark(endPoint, {balloonContent: 'Конечная точка'}));

        if (currentLat !== null && currentLon !== null) {
            var currentPoint = [currentLat, currentLon];
            // Добавление текущей позиции водителя стрелкой
            var driverPlacemark = new ymaps.Placemark(currentPoint, {
                balloonContent: 'Текущая позиция водителя'
            }, {
                preset: 'islands#geolocationIcon', // Использование предустановленной иконки стрелки
                iconColor: '#1E98FF'
            });
            map.geoObjects.add(driverPlacemark);
        }

        if (startLat !== 0 && startLon !== 0 && endLat !== 0 && endLon !== 0) {
            var multiRoute = new ymaps.multiRouter.MultiRoute({
                referencePoints: [
                    startPoint,
                    endPoint
                ],
                params: {
                    results: 1
                }
            }, {
                boundsAutoApply: true
            });
            map.geoObjects.add(multiRoute);
        }

        // Принудительное обновление размеров карты
    }

    function parseFloatOrDefault(value, defaultValue) {
        var parsedValue = parseFloat(value);
        return isNaN(parsedValue) ? defaultValue : parsedValue;
    }
});
