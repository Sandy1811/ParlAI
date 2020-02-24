import React from "react";
import _ from "lodash";

import {
  Glyphicon,
  Row,
  Col,
  FormControl,
  Button,
  ButtonGroup,
  InputGroup,
  FormGroup,
  MenuItem,
  DropdownButton,
  Badge,
  Checkbox,
  Radio,
  Popover,
  Overlay,
  Nav,
  NavItem,
  ControlLabel,
  Form,
  Tabs,
  Tab,
  HelpBlock
} from "react-bootstrap";
import * as constants from "./constants";

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

function ControlLabelWithRemove(props) {
  return (
    <ControlLabel>
      {props.property}
      <Button
        style={{ border: 0, padding: "3px 6px" }}
        onClick={() => props.onRemove(props.category, props.property)}
      >
        <Glyphicon glyph="remove" />
      </Button>

    </ControlLabel>
  );
}

export function jsonToForm(json, category, activeFormFields, removeFormField) {
  const inputByName = _.keyBy(json.input, "Name");

  return activeFormFields.map(formFieldName => {
    const input = inputByName[formFieldName];
    const isRequired = json.required.indexOf(input.Name) >= 0;
    const controlLabelWithRemove = (
      <ControlLabelWithRemove
        property={input.Name}
        name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
        category={category}
        onRemove={removeFormField}
      />
    );
    switch (input.Type) {
      case "LongString":
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              required={isRequired}
              name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
              componentClass="textarea"
              placeholder="textarea"
            />
          </FormGroup>
        );

      case "ShortString":
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
              required={isRequired}
              componentClass="input"
              style={{ maxWidth: 400 }}
            />
          </FormGroup>
        );
      case "Categorical":
      case "CategoricalMultiple":
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              required={isRequired}
              name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
              componentClass="select"
              placeholder="select"
              multiple={input.Type == "CategoricalMultiple"}
            >
              {input.Categories.map((category, idx) =>
                <option key={`${category}-idx`} value={category}>
                  {category}
                </option>
              )}
            </FormControl>
          </FormGroup>
        );
      case "Boolean":
        return (
          <FormGroup>
            <Checkbox
              name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
              required={isRequired}
              inline
            >
              {input.Name}
            </Checkbox>
            <Button
              style={{ border: 0, padding: "3px 6px" }}
              onClick={() => removeFormField(category, input.Name)}
            >
              <Glyphicon glyph="remove" />
            </Button>
          </FormGroup>
        );
      case "Integer":
        // handle Min and Max
        return (
          <FormGroup controlId="formControlsNumber">
            {controlLabelWithRemove}
            <div>
              <FormControl
                required={isRequired}
                name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
                componentClass="select"
                placeholder="is"
                style={{ maxWidth: 130, display: "inline-block" }}
              >
                <option value="is">is</option>
                <option value="is_greater_than">is greater than</option>
                <option value="is_not">is not</option>
              </FormControl>
              <FormControl
                required={isRequired}
                name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
                componentClass="input"
                type="number"
                style={{
                  maxWidth: 200,
                  display: "inline-block",
                  marginLeft: 20
                }}
              />
            </div>
          </FormGroup>
        );
    }
  });
}
