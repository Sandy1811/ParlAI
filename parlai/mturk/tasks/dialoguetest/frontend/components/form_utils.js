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
        style={{ border: 0, padding: "3px 6px", background: "transparent" }}
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
        const uiLogicInfo = {
          Categorical: {
            is_equal_to: "SingleSelect",
            is_one_of: "MultiSelect"
            // Todo: Probably easier if the back-end provides "is_not_equal" ?
            // is_not: "SingleSelect"
          },
          CategoricalMultiple: {
            is_equal_to: "MultiSelect",
            contains: "SingleSelect",
            contain_all_of: "MultiSelect",
            contain_at_least_one_of: "MultiSelect"
          }
        }[input.Type];

        const operatorUi = (
          <FormControl
            name={`${constants.FIELD_OPERATOR_PREFIX}${input.Name}`}
            componentClass="select"
            placeholder={Object.keys(uiLogicInfo)[0]}
            style={{ maxWidth: 130, display: "inline-block" }}
          >
            {Object.keys(uiLogicInfo).map(key =>
              <option value={key}>{key.replace(/_/g, " ")}</option>
            )}
          </FormControl>
        );

        const isMultiple = true;

        return (
          <FormGroup>
            {controlLabelWithRemove}
            <div>
              {operatorUi}
              <FormControl
                required={isRequired}
                name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
                componentClass="select"
                placeholder="select"
                multiple={isMultiple}
                style={{ maxWidth: 200 }}
              >
                {input.Categories.map((category, idx) =>
                  <option key={`${category}-idx`} value={category}>
                    {category}
                  </option>
                )}
              </FormControl>
            </div>
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
              style={{
                border: 0,
                padding: "3px 6px",
                background: "transparent"
              }}
              onClick={() => removeFormField(category, input.Name)}
            >
              <Glyphicon glyph="remove" />
            </Button>
          </FormGroup>
        );
      case "Integer":
        // TODO (high-pri): more operators for all data types

        const { Min, Max } = input;

        return (
          <FormGroup controlId="formControlsNumber">
            {controlLabelWithRemove}
            <div>
              <FormControl
                required={isRequired}
                name={`${constants.FIELD_OPERATOR_PREFIX}${input.Name}`}
                componentClass="select"
                placeholder="is"
                style={{ maxWidth: 130, display: "inline-block" }}
              >
                <option value="is_equal_to">is equal to</option>
                <option value="is_greater_than">is greater than</option>
                <option value="is_less_than">is less than</option>
                <option value="is_not">is not</option>
              </FormControl>
              <FormControl
                required={isRequired}
                name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
                componentClass="input"
                type="number"
                min={Min}
                max={Max}
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
