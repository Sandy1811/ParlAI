/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

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

import $ from "jquery";

// Copied from https://github.com/RasaHQ/data-collection-2020/blob/master/apis/apis/apartment_search.json
const apartmentJson = {
  input: [
    { Name: "Level", Type: "Integer", Min: 0, Max: 15 },
    {
      Name: "MaxLevel",
      Type: "Integer",
      Min: 0,
      Max: 15
    },
    { Name: "HasBalcony", Type: "Boolean" },
    {
      Name: "BalconySide",
      Type: "Categorical",
      Categories: ["east", "north", "south", "west"]
    },
    {
      Name: "HasElevator",
      Type: "Boolean"
    },
    { Name: "NumRooms", Type: "Integer", Min: 1, Max: 7 },
    {
      Name: "FloorSquareMeters",
      Type: "Integer",
      Min: 10,
      Max: 350
    },
    {
      Name: "NearbyPOIs",
      Type: "CategoricalMultiple",
      Categories: ["School", "TrainStation", "Park"]
    },
    {
      Name: "Name",
      Type: "Categorical",
      Categories: [
        "One on Center Apartments",
        "Shadyside Apartments",
        "North Hill Apartments"
      ]
    }
  ],
  output: [
    { Name: "Level", Type: "Integer", Min: 0, Max: 15 },
    {
      Name: "MaxLevel",
      Type: "Integer",
      Min: 0,
      Max: 15
    },
    { Name: "HasBalcony", Type: "Boolean" },
    {
      Name: "BalconySide",
      Type: "Categorical",
      Categories: ["east", "north", "south", "west"]
    },
    {
      Name: "HasElevator",
      Type: "Boolean"
    },
    { Name: "NumRooms", Type: "Integer", Min: 1, Max: 7 },
    {
      Name: "FloorSquareMeters",
      Type: "Integer",
      Min: 10,
      Max: 350
    },
    {
      Name: "NearbyPOIs",
      Type: "CategoricalMultiple",
      Categories: ["School", "TrainStation", "Park"]
    },
    {
      Name: "Name",
      Type: "Categorical",
      Categories: [
        "One on Center Apartments",
        "Shadyside Apartments",
        "North Hill Apartments"
      ]
    }
  ],
  required: ["NumRooms"],
  db: "apartment",
  function: "generic_sample",
  returns_count: true
};

const hotelSearch = {
  input: [
    {
      Name: "Name",
      Type: "Categorical",
      Categories: [
        "Shadyside Inn",
        "Hilton Hotel",
        "Hyatt Hotel",
        "Old Town Inn"
      ]
    },
    {
      Name: "Cost",
      Type: "Categorical",
      Categories: ["Cheap", "Moderate", "Expensive"]
    },
    { Name: "TakesReservations", Type: "Boolean" },
    { Name: "Service", Type: "Boolean" },
    { Name: "AverageRating", Type: "Integer", Min: 1, Max: 5 },
    {
      Name: "ServiceStartHour",
      Type: "Integer",
      Min: 6,
      Max: 10,
      Enabled: '!lambda p: p["Service"]'
    },
    {
      Name: "ServiceStopHour",
      Type: "Integer",
      Min: 15,
      Max: 23,
      Enabled: '!lambda p: p["Service"]'
    },
    {
      Name: "Location",
      Type: "Categorical",
      Categories: ["South", "West", "East", "North", "Center"]
    }
  ],
  output: [
    {
      Name: "Name",
      Type: "Categorical",
      Categories: [
        "Shadyside Inn",
        "Hilton Hotel",
        "Hyatt Hotel",
        "Old Town Inn"
      ]
    },
    {
      Name: "Cost",
      Type: "Categorical",
      Categories: ["Cheap", "Moderate", "Expensive"]
    },
    { Name: "TakesReservations", Type: "Boolean" },
    { Name: "Service", Type: "Boolean" },
    { Name: "AverageRating", Type: "Integer", Min: 1, Max: 5 },
    {
      Name: "ServiceStartHour",
      Type: "Integer",
      Min: 6,
      Max: 10,
      Enabled: '!lambda p: p["Service"]'
    },
    {
      Name: "ServiceStopHour",
      Type: "Integer",
      Min: 15,
      Max: 23,
      Enabled: '!lambda p: p["Service"]'
    },
    {
      Name: "Location",
      Type: "Categorical",
      Categories: ["South", "West", "East", "North", "Center"]
    }
  ],
  required: [],
  db: "hotel",
  function: "generic_sample",
  returns_count: true
};

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

function FormKitchenSink() {
  return (
    <div>
      <FieldGroup
        id="formControlsText"
        type="text"
        label="Text"
        placeholder="Enter text"
      />
      <FormGroup>
        <Checkbox inline>1</Checkbox> <Checkbox inline>2</Checkbox>{" "}
        <Checkbox inline>3</Checkbox>
      </FormGroup>
      <FormGroup>
        <Radio name="radioGroup" inline>
          1
        </Radio>
        {" "}
        <Radio name="radioGroup" inline>
          2
        </Radio>
        {" "}
        <Radio name="radioGroup" inline>
          3
        </Radio>
      </FormGroup>

      <FormGroup controlId="formControlsTextarea">
        <ControlLabel>Textarea</ControlLabel>
        <FormControl componentClass="textarea" placeholder="textarea" />
      </FormGroup>
    </div>
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

function jsonToForm(json, category, activeFormFields, removeFormField) {
  const inputByName = _.keyBy(json.input, "Name");

  return activeFormFields.map(formFieldName => {
    const input = inputByName[formFieldName];
    const isRequired = json.required.indexOf(input.Name) >= 0;
    const controlLabelWithRemove = (
      <ControlLabelWithRemove
        property={input.Name}
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
              componentClass="select"
              placeholder="select"
              multiple={input.Type == "CategoricalMultiple"}
            >
              {input.Categories.map(category =>
                <option value={category}>{category}</option>
              )}
            </FormControl>
          </FormGroup>
        );
      case "Boolean":
        return (
          <FormGroup>
            <Checkbox required={isRequired} inline>{input.Name}</Checkbox>
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
                componentClass="select"
                placeholder="is"
                style={{ maxWidth: 130, display: "inline-block" }}
              >
                <option value="select">is</option>
                <option value="other">is greater than</option>
                <option value="other">is not</option>
              </FormControl>
              <FormControl
                required={isRequired}
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

function QueryForm(props) {
  const { category, addFormField, removeFormField, activeFormFields } = props;
  const json = apartmentJson;

  return (
    <form onSubmit={() => {}}>
      <FormGroup>
        <div>
          <FormControl
            componentClass="select"
            style={{ maxWidth: 130, display: "inline-block" }}
          >
            {json.input.map(input =>
              <option value={input.Name}>{input.Name}</option>
            )}
          </FormControl>
          <Button
            className="btn"
            onClick={() => {
              addFormField(category, "NumRooms");
            }}
            style={{ marginLeft: 20 }}
          >
            Add Field
          </Button>
        </div>
      </FormGroup>
      <hr />
      {jsonToForm(json, category, activeFormFields, removeFormField)}

      <Button
        className="btn btn-primary"
        disabled={props.chat_state !== "text_input"}
        onClick={() => {
          console.log("sending ? {}");
          props.onMessageSend("? {}", {}, () => console.log("done"));
        }}
      >
        Find example
      </Button>
    </form>
  );
}

// Create custom components
class EvaluatorIdleResponse extends React.Component {
  render() {
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left"
    };

    return (
      <div
        id="response-type-idle"
        className="response-type-module"
        style={pane_style}
      >
        <span>
          Pay attention to the conversation above, as you'll need to evaluate.
        </span>
      </div>
    );
  }
}

class NumericResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = { textval: "", sending: false };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Only change in the active status of this component should cause a
    // focus event. Not having this would make the focus occur on every
    // state update (including things like volume changes)
    if (this.props.active && !prevProps.active) {
      $("input#id_text_input").focus();
    }
    this.props.onInputResize();
  }

  tryMessageSend() {
    if (this.state.textval != "" && this.props.active && !this.state.sending) {
      this.setState({ sending: true });
      this.props.onMessageSend(this.state.textval, {}, () =>
        this.setState({ textval: "", sending: false })
      );
    }
  }

  handleKeyPress(e) {
    if (e.key === "Enter") {
      this.tryMessageSend();
      e.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
    }
  }

  updateValue(amount) {
    // if ((amount != "" && isNaN(amount)) || amount < 0) {
    //   return;
    // }
    // amount = amount == "" ? 0 : amount;
    this.setState({ textval: "" + amount });
  }

  render() {
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left",
      width: "100%"
    };
    let input_style = {
      height: "50px",
      width: "100%",
      display: "block",
      float: "left"
    };
    let submit_style = {
      width: "100px",
      height: "100%",
      fontSize: "16px",
      float: "left",
      marginLeft: "10px",
      padding: "0px"
    };

    let text_input = (
      <FormControl
        type="text"
        id="id_text_input"
        style={{
          width: "80%",
          height: "100%",
          float: "left",
          fontSize: "16px"
        }}
        value={this.state.textval}
        placeholder="Please enter here..."
        onKeyPress={e => this.handleKeyPress(e)}
        onChange={e => this.updateValue(e.target.value)}
        disabled={!this.props.active || this.state.sending}
      />
    );

    // TODO attach send message callback
    let submit_button = (
      <Button
        className="btn btn-primary"
        style={submit_style}
        id="id_send_msg_button"
        disabled={
          this.state.textval == "" || !this.props.active || this.state.sending
        }
        onClick={() => this.tryMessageSend()}
      >
        Send
      </Button>
    );

    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={pane_style}
      >
        <div style={input_style}>
          {text_input}
          {submit_button}
        </div>
      </div>
    );
  }
}

class EvaluationResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = { textval: "", sending: false };
  }

  tryMessageSend(value) {
    if (this.props.active && !this.state.sending) {
      this.setState({ sending: true });
      this.props.onMessageSend(value, {}, () =>
        this.setState({ textval: "", sending: false })
      );
    }
  }

  render() {
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left",
      width: "100%"
    };
    let input_style = {
      height: "50px",
      width: "100%",
      display: "block",
      float: "left"
    };
    let submit_style = {
      width: "100px",
      height: "100%",
      fontSize: "16px",
      float: "left",
      marginLeft: "10px",
      padding: "0px"
    };

    let reject_button = (
      <Button
        className="btn btn-danger"
        style={submit_style}
        id="id_reject_chat_button"
        disabled={!this.props.active || this.state.sending}
        onClick={() => this.tryMessageSend("reject")}
      >
        Reject!
      </Button>
    );

    let approve_button = (
      <Button
        className="btn btn-success"
        style={submit_style}
        id="id_approve_chat_button"
        disabled={!this.props.active || this.state.sending}
        onClick={() => this.tryMessageSend("approve")}
      >
        Approve!
      </Button>
    );

    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={pane_style}
      >
        <div style={input_style}>
          {reject_button}
          {approve_button}
        </div>
      </div>
    );
  }
}

const leftSideCategories = [
  "Apartments",
  "Hotels",
  "Flights",
  "Artifacts",
  "Trains"
];

class LeftPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      current_pane: "instruction",
      last_update: 0,
      selectedTabKey: 2,
      addedFormFieldsByCategory: Object.fromEntries(
        leftSideCategories.map(category => [category, []])
      )
    };
  }

  addFormField = (category, fieldName) => {
    this.setState({
      addedFormFieldsByCategory: {
        ...this.state.addedFormFieldsByCategory,
        [category]: [
          ...this.state.addedFormFieldsByCategory[category],
          fieldName
        ]
      }
    });
  };

  removeFormField = (category, fieldName) => {
    this.setState({
      addedFormFieldsByCategory: {
        ...this.state.addedFormFieldsByCategory,
        [category]: _.without(
          this.state.addedFormFieldsByCategory[category],
          fieldName
        )
      }
    });
  };

  static getDerivedStateFromProps(nextProps, prevState) {
    if (
      nextProps.task_data !== undefined &&
      nextProps.task_data.last_update !== undefined &&
      nextProps.task_data.last_update > prevState.last_update
    ) {
      return {
        current_pane: "context",
        last_update: nextProps.task_data.last_update
      };
    } else return null;
  }

  handleSelectTab = key => {
    this.setState({
      selectedTabKey: key
    });
  };

  render() {
    let v_id = this.props.v_id;
    let frame_height = this.props.frame_height;
    let frame_style = {
      height: frame_height + "px",
      backgroundColor: "#fafbfc",
      padding: "30px",
      overflow: "auto"
    };

    let pane_size = this.props.is_cover_page ? "col-xs-12" : "col-xs-4";
    let has_context = this.props.task_data.has_context;

    console.log("this.props", this.props);

    return (
      <div id="left-pane" className={pane_size} style={frame_style}>
        <Tab.Container
          id="left-tabs-example"
          defaultActiveKey={leftSideCategories[0]}
        >
          <Row className="clearfix">
            <Col sm={3} style={{ marginTop: 50 }}>
              <Nav bsStyle="pills" stacked>
                {leftSideCategories.map(tabName =>
                  <NavItem eventKey={tabName}>{tabName}</NavItem>
                )}
              </Nav>
            </Col>
            <Col sm={9}>
              <Tab.Content animation={false} mountOnEnter={true}>
                {leftSideCategories.map(categoryName => {
                  return (
                    <Tab.Pane
                      eventKey={categoryName}
                      animation={false}
                      mountOnEnter={true}
                    >
                      <Tabs
                        eventKey={this.state.selectedTabKey}
                        onSelect={this.handleSelectTab}
                        animation={false}
                      >
                        <Tab eventKey={1} title="Your Instruction Schema">
                          Instruction Schema Image
                        </Tab>
                        <Tab eventKey={2} title="Knowledge Base">
                          <h4>User's requirements for {categoryName}:</h4>
                          <QueryForm
                            {...this.props}
                            category={categoryName}
                            addFormField={this.addFormField}
                            removeFormField={this.removeFormField}
                            activeFormFields={
                              this.state.addedFormFieldsByCategory[categoryName]
                            }
                          />
                        </Tab>
                      </Tabs>
                    </Tab.Pane>
                  );
                })}
              </Tab.Content>
            </Col>
          </Row>
        </Tab.Container>
        {this.props.children}
      </div>
    );
  }
}

// Package components
var IdleResponseHolder = {
  // default: leave blank to use original default when no ids match
  Wizard: EvaluatorIdleResponse
};

var TextResponseHolder = {
  // default: leave blank to use original default when no ids match
  // Wizard: EvaluationResponse,
  User: NumericResponse
};

export default {
  // ComponentName: CustomReplacementComponentMap
  XTextResponse: TextResponseHolder,
  XIdleResponse: IdleResponseHolder,
  XLeftPane: {
    Wizard: LeftPane
  }
};
