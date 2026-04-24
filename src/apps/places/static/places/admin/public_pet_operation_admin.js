(function () {
  function parseConfig() {
    var node = document.getElementById("public-pet-operation-admin-config");
    if (!node) {
      return null;
    }

    try {
      return JSON.parse(node.textContent || "{}");
    } catch (_error) {
      return null;
    }
  }

  function normalizeText(value) {
    return (value || "")
      .toString()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim()
      .toLowerCase();
  }

  function setStatus(statusNode, message, tone) {
    if (!statusNode) {
      return;
    }

    statusNode.textContent = message || "";
    statusNode.classList.remove("is-warning", "is-error", "is-success");
    if (tone) {
      statusNode.classList.add(tone);
    }
  }

  function replaceOptions(selectNode, values, selectedValue) {
    if (!selectNode) {
      return;
    }

    selectNode.innerHTML = "";
    values.forEach(function (value) {
      var option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      option.selected = value === selectedValue;
      selectNode.appendChild(option);
    });
  }

  function initializeDependentSelects(regions, regionInput, communeInput) {
    if (!regionInput || !communeInput) {
      return;
    }

    var regionMap = new Map(
      regions.map(function (item) {
        return [item.region, item.communes];
      }),
    );

    function syncCommunes(keepCurrentValue) {
      var currentRegion = regionInput.value;
      var communes = regionMap.get(currentRegion) || [];
      var currentCommune = keepCurrentValue ? communeInput.value : "";
      if (currentCommune && communes.indexOf(currentCommune) === -1) {
        currentCommune = "";
      }
      replaceOptions(communeInput, communes, currentCommune || communes[0] || "");
    }

    syncCommunes(true);
    regionInput.addEventListener("change", function () {
      syncCommunes(false);
    });
  }

  function loadGoogleMaps(apiKey) {
    if (!apiKey) {
      return Promise.reject(
        new Error("Falta GOOGLE_MAPS_API_KEY. Configura la clave para usar el autocompletado."),
      );
    }

    if (window.google && window.google.maps && window.google.maps.places) {
      return Promise.resolve(window.google.maps);
    }

    if (window.__publicPetOperationsGoogleMapsPromise) {
      return window.__publicPetOperationsGoogleMapsPromise;
    }

    window.__publicPetOperationsGoogleMapsPromise = new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src =
        "https://maps.googleapis.com/maps/api/js?key=" +
        encodeURIComponent(apiKey) +
        "&libraries=places&language=es&region=CL";
      script.async = true;
      script.defer = true;
      script.onload = function () {
        if (window.google && window.google.maps && window.google.maps.places) {
          resolve(window.google.maps);
        } else {
          reject(
            new Error(
              "Google Maps cargó sin la librería necesaria. Revisa que Maps JavaScript API y Places API estén habilitadas.",
            ),
          );
        }
      };
      script.onerror = function () {
        reject(new Error("No se pudo cargar Google Maps. Revisa la clave y las restricciones del dominio."));
      };
      document.head.appendChild(script);
    });

    return window.__publicPetOperationsGoogleMapsPromise;
  }

  function initializeMap(mapNode, latitude, longitude) {
    if (!mapNode || !window.google || !window.google.maps || !window.google.maps.Map) {
      return null;
    }

    var hasInitialPoint = typeof latitude === "number" && typeof longitude === "number";
    var center = hasInitialPoint ? { lat: latitude, lng: longitude } : { lat: -33.4489, lng: -70.6693 };
    var map = new window.google.maps.Map(mapNode, {
      center: center,
      zoom: hasInitialPoint ? 16 : 11,
      streetViewControl: false,
      mapTypeControl: false,
      fullscreenControl: false,
    });

    var marker = null;

    if (hasInitialPoint) {
      marker = new window.google.maps.Marker({
        map: map,
        position: center,
      });
    }

    return {
      setPoint: function (lat, lng) {
        var point = { lat: lat, lng: lng };
        if (marker) {
          marker.setPosition(point);
        } else {
          marker = new window.google.maps.Marker({
            map: map,
            position: point,
          });
        }
        map.setCenter(point);
        map.setZoom(16);
      },
      clearPoint: function () {
        if (marker) {
          marker.setMap(null);
          marker = null;
        }
        map.setCenter({ lat: -33.4489, lng: -70.6693 });
        map.setZoom(11);
      },
    };
  }

  function initializeAutocomplete(config, regionInput, communeInput, addressInput, latitudeInput, longitudeInput, mapController, statusNode) {
    if (!addressInput || !latitudeInput || !longitudeInput) {
      return;
    }

    var autocomplete = new window.google.maps.places.Autocomplete(addressInput, {
      componentRestrictions: { country: "cl" },
      fields: ["address_components", "formatted_address", "geometry", "name"],
      types: ["geocode"],
    });

    var lastSelectedAddress = addressInput.value;

    addressInput.addEventListener("input", function () {
      if (addressInput.value === lastSelectedAddress) {
        return;
      }

      latitudeInput.value = "";
      longitudeInput.value = "";
      mapController.clearPoint();
      setStatus(
        statusNode,
        "Selecciona una sugerencia de Google para confirmar las coordenadas antes de publicar.",
        "is-warning",
      );
    });

    autocomplete.addListener("place_changed", function () {
      var place = autocomplete.getPlace();
      if (!place || !place.geometry || !place.geometry.location) {
        setStatus(
          statusNode,
          "La sugerencia seleccionada no entregó coordenadas. Intenta con otra opción.",
          "is-error",
        );
        return;
      }

      var lat = place.geometry.location.lat();
      var lng = place.geometry.location.lng();

      latitudeInput.value = lat.toFixed(6);
      longitudeInput.value = lng.toFixed(6);
      addressInput.value = place.formatted_address || place.name || addressInput.value;
      lastSelectedAddress = addressInput.value;

      var addressComponents = place.address_components || [];
      var regionComponent = addressComponents.find(function (component) {
        return component.types.indexOf("administrative_area_level_1") !== -1;
      });
      var communeComponent = addressComponents.find(function (component) {
        return (
          component.types.indexOf("administrative_area_level_3") !== -1 ||
          component.types.indexOf("locality") !== -1
        );
      });

      if (regionComponent && regionInput) {
        var matchedRegion = config.regions.find(function (item) {
          return normalizeText(item.region) === normalizeText(regionComponent.long_name);
        });
        if (matchedRegion) {
          regionInput.value = matchedRegion.region;
          regionInput.dispatchEvent(new Event("change"));
        }
      }

      if (communeComponent && communeInput) {
        var communes = Array.from(communeInput.options).map(function (option) {
          return option.value;
        });
        var matchedCommune = communes.find(function (commune) {
          return normalizeText(commune) === normalizeText(communeComponent.long_name);
        });
        if (matchedCommune) {
          communeInput.value = matchedCommune;
        }
      }

      mapController.setPoint(lat, lng);
      setStatus(
        statusNode,
        "Dirección confirmada. Se guardarán las coordenadas junto al operativo.",
        "is-success",
      );
    });

    if (latitudeInput.value && longitudeInput.value) {
      setStatus(
        statusNode,
        "Coordenadas cargadas. Si cambias la dirección, vuelve a elegir una sugerencia antes de guardar.",
        "is-success",
      );
      return;
    }

    setStatus(
      statusNode,
      "Escribe la dirección y elige una sugerencia válida de Google para completar latitud y longitud.",
      "is-warning",
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var config = parseConfig();
    if (!config) {
      return;
    }

    var wrapper = document.querySelector(".public-pet-operation-admin");
    if (!wrapper) {
      return;
    }

    var mapNode = wrapper.querySelector('[data-role="map"]');
    var statusNode = wrapper.querySelector('[data-role="status"]');
    var regionInput = document.getElementById("id_region");
    var communeInput = document.getElementById("id_commune");
    var addressInput = document.getElementById("id_address");
    var latitudeInput = document.getElementById("id_latitude");
    var longitudeInput = document.getElementById("id_longitude");

    initializeDependentSelects(config.regions || [], regionInput, communeInput);

    loadGoogleMaps(config.googleMapsApiKey)
      .then(function () {
        var initialLatitude = latitudeInput && latitudeInput.value ? Number(latitudeInput.value) : config.latitude;
        var initialLongitude =
          longitudeInput && longitudeInput.value ? Number(longitudeInput.value) : config.longitude;
        var mapController = initializeMap(mapNode, initialLatitude, initialLongitude);
        if (!mapController) {
          setStatus(
            statusNode,
            "No se pudo inicializar el mapa. Revisa la configuración de Google Maps.",
            "is-error",
          );
          return;
        }

        initializeAutocomplete(
          config,
          regionInput,
          communeInput,
          addressInput,
          latitudeInput,
          longitudeInput,
          mapController,
          statusNode,
        );
      })
      .catch(function (error) {
        setStatus(
          statusNode,
          error && error.message ? error.message : "No se pudo cargar Google Maps.",
          "is-error",
        );
      });
  });
})();
